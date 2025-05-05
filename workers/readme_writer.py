import sys
import time
import pytz
import toml
from datetime import datetime

from utils import get_daily_papers_by_keyword_with_retries, generate_table, back_up_files,\
    restore_files, remove_backups, get_daily_date
from db.db_repo import DatabaseRepository


class ReadmeWriter:
    """负责生成README和ISSUE_TEMPLATE文件的类"""
    
    def __init__(self, db_param=None):
        """初始化ReadmeWriter"""
        # 加载配置
        self.config = toml.load('config.toml')
        self.beijing_timezone = pytz.timezone('Asia/Shanghai')
        self.db = db_param if db_param else DatabaseRepository()
        self.current_date = datetime.now(self.beijing_timezone).strftime("%Y-%m-%d")
        
        # 配置参数
        self.max_result = self.config['max_result']
        self.issues_result = self.config['issues_result']
        self.column_names = ["Title", "Link", "Abstract", "Date", "Comment"]
    
    def get_last_update_date(self):
        """获取上次更新日期"""
        try:
            with open("README.md", "r") as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if "Last update:" in line:
                        return line.split(": ")[1].strip()
        except Exception as e:
            print(f"获取上次更新日期失败: {e}")
        return None
    
    def should_update(self):
        """判断是否需要更新"""
        last_update_date = self.get_last_update_date()
        if last_update_date and last_update_date == self.current_date:
            print(f"今天已经更新过了: {self.current_date}")
            return False
        return True
    
    def write_readme(self, papers_by_keyword):
        """写入README和ISSUE_TEMPLATE文件"""
        try:
            # 备份文件
            back_up_files()
            
            # 获取关键词列表
            keywords = list(papers_by_keyword.keys())
            
            # 写入README.md
            print("开始写入README")
            f_rm = open("README.md", "w", encoding="utf-8")
            f_rm.write("# Daily Papers\n")
            f_rm.write("The project automatically fetches the latest papers from arXiv based on keywords.\n\nThe subheadings in the README file represent the search keywords.\n\nOnly the most recent articles for each keyword are retained, up to a maximum of 100 papers.\n\nYou can click the 'Watch' button to receive daily email notifications.\n\nLast update: {0}\n\n".format(self.current_date))
            
            # 写入ISSUE_TEMPLATE.md
            print("开始写入ISSUE_TEMPLATE")
            f_is = open(".github/ISSUE_TEMPLATE.md", "w", encoding="utf-8")
            f_is.write("---\n")
            f_is.write("title: Latest {0} Papers - {1}\n".format(self.issues_result, get_daily_date()))
            f_is.write("labels: documentation\n")
            f_is.write("---\n")
            
            # 为每个关键词生成表格
            for keyword in keywords:
                papers = papers_by_keyword.get(keyword, [])
                if not papers:
                    continue
                papers = self.paper_complete(papers)
                f_rm.write("## {0}\n".format(keyword))
                f_is.write("## {0}\n".format(keyword))
                
                rm_table = generate_table(papers)
                is_table = generate_table(papers[:self.issues_result], ignore_keys=["Abstract"])
                
                f_rm.write(rm_table)
                f_rm.write("\n\n")
                f_is.write(is_table)
                f_is.write("\n\n")
            
            # 关闭文件
            f_rm.close()
            f_is.close()
            
            # 删除备份
            remove_backups()
            print("README和ISSUE_TEMPLATE文件已更新")
            return True
            
        except Exception as e:
            print(f"写入README失败: {e}")
            restore_files()
            return False
    
    def process_papers(self, papers_by_keyword):
        """处理论文数据并写入README"""
        if not papers_by_keyword:
            print("没有论文数据可写入")
            return False
        
        return self.write_readme(papers_by_keyword)
    
    def close(self):
        """关闭数据库连接"""
        if self.db:
            self.db.close()
            
    def paper_complete(self, papers):
        # 确保每个paper都有必要的字段
        for paper in papers:
            if 'Title' not in paper:
                paper['Title'] = 'Unknown Title'
            if 'Abstract' not in paper:
                paper['Abstract'] = ''
            if 'Date' not in paper:
                paper['Date'] = self.current_date
            if 'Comment' not in paper:
                paper['Comment'] = ''
            if 'Link' not in paper:
                paper['Link'] = ''  # 添加空的Link字段
        return papers