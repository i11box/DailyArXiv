import os
import sys
import toml
import pymysql
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

# 读取配置文件
config = toml.load('config.toml')

# 数据库连接配置
DB_CONFIG = {
    'host': config['DB_HOST'],
    'port': config['DB_PORT'],
    'user': config['DB_USER'],
    'password': config['DB_PASSWORD'],
    'db': config['DB_NAME'],
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

class DatabaseManager:
    """数据库管理类，提供增删改查操作"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.conn = None
        self.connect()
    
    def connect(self):
        """连接到数据库"""
        try:
            print(f"尝试连接数据库，配置: {DB_CONFIG}")
            self.conn = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=str(DB_CONFIG['password']),  # 确保密码是字符串
                database=DB_CONFIG['db'],
                charset=DB_CONFIG['charset'],
                cursorclass=DB_CONFIG['cursorclass']
            )
            print("数据库连接成功")
            return True
        except pymysql.Error as e:
            print(f"数据库连接失败，错误代码: {e.args[0]}")
            print(f"错误信息: {e.args[1]}")
            print("请检查以下配置:")
            print(f"1. MySQL服务是否运行 (net start mysql)")
            print(f"2. 主机: {DB_CONFIG['host']}")
            print(f"3. 端口: {DB_CONFIG['port']}")
            print(f"4. 用户名: {DB_CONFIG['user']}")
            print(f"5. 数据库: {DB_CONFIG['db']} 是否存在")
            return False
        except Exception as e:
            print(f"未知错误: {type(e)} - {str(e)}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行查询操作"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"查询执行失败: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作（插入、更新、删除）"""
        try:
            with self.conn.cursor() as cursor:
                affected_rows = cursor.execute(query, params or ())
                self.conn.commit()
                return affected_rows
        except Exception as e:
            self.conn.rollback()
            print(f"更新执行失败: {e}")
            return 0
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """执行插入操作并返回自增ID"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params or ())
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"插入执行失败: {e}")
            return 0


class PaperRepository:
    """论文数据仓库，提供论文相关的数据库操作"""
    
    def __init__(self, db_manager: DatabaseManager):
        """初始化论文仓库"""
        self.db = db_manager
    
    def add_paper(self, paper: Dict[str, Any]) -> int:
        """添加论文记录"""
        query = """
        INSERT INTO papers (title, abstract, link, comment, date, keyword)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            paper.get('title'),
            paper.get('abstract'),
            paper.get('link', ''),  # 添加link字段
            paper.get('comment', ''),
            paper.get('date'),
            paper.get('keyword', '')  # 添加keyword字段
        )
        return self.db.execute_insert(query, params)
    
    def update_paper(self, paper_id: int, paper: Dict[str, Any]) -> int:
        """更新论文记录"""
        query = """
        UPDATE papers
        SET title = %s, abstract = %s, comment = %s, date = %s
        WHERE id = %s
        """
        params = (
            paper.get('title'),
            paper.get('abstract'),
            paper.get('authors') if isinstance(paper.get('authors'), str) else ','.join(paper.get('authors', [])),
            paper.get('link'),
            paper.get('comment', ''),
            paper.get('date'),
            paper.get('arxiv_id'),
            paper_id
        )
        return self.db.execute_update(query, params)
    
    def delete_paper(self, paper_id: int) -> int:
        """删除论文记录"""
        query = "DELETE FROM papers WHERE id = %s"
        return self.db.execute_update(query, (paper_id,))
    
    def get_paper_by_id(self, paper_id: int) -> Optional[Dict]:
        """根据ID获取论文"""
        query = "SELECT * FROM papers WHERE id = %s"
        results = self.db.execute_query(query, (paper_id,))
        return results[0] if results else None
    
    def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[Dict]:
        """根据arXiv ID获取论文"""
        query = "SELECT * FROM papers WHERE arxiv_id = %s"
        results = self.db.execute_query(query, (arxiv_id,))
        return results[0] if results else None
    
    def get_papers_by_keyword(self, keyword: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """根据关键词获取论文列表"""
        query = """
        SELECT p.* FROM papers p
        JOIN paper_keywords pk ON p.id = pk.paper_id
        JOIN keywords k ON pk.keyword_id = k.id
        WHERE k.name = %s
        ORDER BY p.date DESC
        LIMIT %s OFFSET %s
        """
        return self.db.execute_query(query, (keyword, limit, offset))
    
    def get_recent_papers(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取最近的论文"""
        query = """
        SELECT * FROM papers
        ORDER BY date DESC
        LIMIT %s OFFSET %s
        """
        return self.db.execute_query(query, (limit, offset))
        
    def get_latest_date(self) -> str:
        """获取最近的论文日期"""
        query = """
        SELECT date FROM papers
        ORDER BY date DESC
        LIMIT 1
        """
        result = self.db.execute_query(query)
        return result[0]['date'] if result else None
        
    def get_papers_by_date(self, date: str) -> List[Dict]:
        """根据日期获取论文"""
        query = """
        SELECT * FROM papers
        WHERE date = %s
        ORDER BY title
        """
        return self.db.execute_query(query, (date,))
    
    def search_papers(self, search_term: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """搜索论文"""
        search_pattern = f"%{search_term}%"
        query = """
        SELECT * FROM papers
        WHERE title LIKE %s OR abstract LIKE %s OR authors LIKE %s
        ORDER BY date DESC
        LIMIT %s OFFSET %s
        """
        return self.db.execute_query(query, (search_pattern, search_pattern, search_pattern, limit, offset))
