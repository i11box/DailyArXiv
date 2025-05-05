import json
import redis
import toml
from datetime import datetime

# 读取配置
config = toml.load('config.toml')

class RedisQueue:
    """Redis队列管理类"""
    
    def __init__(self):
        """初始化Redis连接"""
        self.redis = redis.Redis(
            host=config['REDIS_HOST'],
            port=config['REDIS_PORT'],
            decode_responses=True
        )
        self.task_queue = 'arxiv_tasks'
        self.result_queue = 'arxiv_results'
        self.failed_queue = 'arxiv_failed'
    
    def publish_task(self, keyword, max_results=100, link_type="OR"):
        """发布爬取任务到队列"""
        task_id = f"{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        task = {
            "task_id": task_id,
            "keyword": keyword,
            "max_results": max_results,
            "link_type": link_type,
            "created_at": datetime.now().isoformat()
        }
        self.redis.lpush(self.task_queue, json.dumps(task))
        print(f"任务已发布: {task_id}")
        return task_id
    
    def get_task(self, timeout=0):
        """获取任务，timeout=0表示无限等待"""
        result = self.redis.brpop(self.task_queue, timeout)
        if result:
            return json.loads(result[1])
        return None
    
    def publish_result(self, task_id, papers):
        """发布处理结果"""
        result = {
            "task_id": task_id,
            "papers_count": len(papers),
            "completed_at": datetime.now().isoformat()
        }
        self.redis.lpush(self.result_queue, json.dumps(result))
    
    def publish_failed_task(self, task_id, error):
        """发布失败任务"""
        failed_task = {
            "task_id": task_id,
            "error": str(error),
            "failed_at": datetime.now().isoformat()
        }
        self.redis.lpush(self.failed_queue, json.dumps(failed_task))
    
    def get_queue_length(self, queue_name):
        """获取队列长度"""
        return self.redis.llen(queue_name)
    
    def clear_queue(self, queue_name):
        """清空队列"""
        self.redis.delete(queue_name)
        
    def start_task(self, keywords, max_results=100):
        try:
            for keyword in keywords:
                # for keyword with only one word, We search for papers containing this keyword in both the title and abstract.
                link = "AND" if len(keyword.split()) == 1 else "OR"
                self.publish_task(keyword, link_type=link, max_results=max_results)
        except Exception as e:
            print(f"发布任务失败: {str(e)}")
            return False