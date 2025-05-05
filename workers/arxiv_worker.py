import sys
import time
import toml
from db.redis_queue import RedisQueue
from db.db_repo import DatabaseRepository
from utils import get_daily_papers_by_keyword_with_retries

class ArxivWorker:
    def __init__(self, db_param = None,rq_param=None) -> None:
        config = toml.load('config.toml')
        self.db = db_param if db_param else DatabaseRepository() 
        self.rq = RedisQueue() if rq_param is None else rq_param
        self.paper_keyword = {} # 键为关键词，值为papers
        self.max_result = config['max_result']
        self.issues_result = config['issues_result']
    def process_task(self, task):
        """处理单个爬取任务"""
        print(f"开始处理任务: {task['task_id']}")
        
        # 获取论文数据
        papers = get_daily_papers_by_keyword_with_retries(
            task['keyword'], 
            ["Title", "Abstract", "Date", "Comment"], 
            self.max_result, 
            task['link_type']
        )
        
        if papers is None:
            print(f"任务失败: {task['task_id']}")
            self.rq.publish_failed_task(task['task_id'], "Failed to get papers")
            return False
        
        self.paper_keyword[task['keyword']] = papers
        
        # 发布结果
        self.rq.publish_result(task['task_id'], papers)
        print(f"任务完成: {task['task_id']}, 获取到 {len(papers)} 篇论文")

        return True

    def run_worker(self, timeout=0, max_idle_time=10):
        """运行工作进程，处理队列中的任务"""
        print("启动arXiv爬虫工作进程...")
        
        try:
            idle_start_time = time.time()
            
            while True:
                try:
                    # 获取任务
                    task = self.rq.get_task(1)  # 使用1秒超时，允许定期检查条件
                    
                    if task:
                        # 重置空闲计时器
                        idle_start_time = time.time()
                        
                        try:
                            self.process_task(task)
                            # 避免被arXiv API封锁
                            time.sleep(5)
                        except Exception as e:
                            print(f"处理任务出错: {str(e)}")
                            self.rq.publish_failed_task(task['task_id'], str(e))
                    else:
                        # 检查是否超过最大空闲时间
                        current_idle_time = time.time() - idle_start_time
                        
                        if max_idle_time > 0 and current_idle_time > max_idle_time:
                            print(f"已空闲{current_idle_time:.1f}秒，超过最大空闲时间{max_idle_time}秒，工作进程退出")
                            break
                        
                        # 如果设置了超时且没有任务，则退出
                        if timeout > 0:
                            print("队列为空，工作进程退出")
                            break
                        
                        print(f"队列为空，已等待{current_idle_time:.1f}秒...")
                        time.sleep(1)  # 短暂睡眠，避免CPU占用过高
                        
                except KeyboardInterrupt:
                    print("检测到键盘中断，工作进程将退出...")
                    break
        
        except Exception as e:
            print(f"工作进程遇到错误: {str(e)}")
        
        print("run_worker: 结束")
    
    def save_papers(self):
        print("save_papers: 开始")
        self.db.save_papers(self.paper_keyword)
        print("save_papers: 结束")