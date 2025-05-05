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
        INSERT INTO papers (title, abstract, authors, link, comment, date, arxiv_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            paper.get('title'),
            paper.get('abstract'),
            paper.get('authors') if isinstance(paper.get('authors'), str) else ','.join(paper.get('authors', [])),
            paper.get('link'),
            paper.get('comment', ''),
            paper.get('date'),
            paper.get('arxiv_id')
        )
        return self.db.execute_insert(query, params)
    
    def update_paper(self, paper_id: int, paper: Dict[str, Any]) -> int:
        """更新论文记录"""
        query = """
        UPDATE papers
        SET title = %s, abstract = %s, authors = %s, link = %s, comment = %s, date = %s, arxiv_id = %s
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


class KeywordRepository:
    """关键词数据仓库，提供关键词相关的数据库操作"""
    
    def __init__(self, db_manager: DatabaseManager):
        """初始化关键词仓库"""
        self.db = db_manager
    
    def add_keyword(self, name: str, description: str = "") -> int:
        """添加关键词"""
        query = """
        INSERT INTO keywords (name, description)
        VALUES (%s, %s)
        """
        return self.db.execute_insert(query, (name, description))
    
    def update_keyword(self, keyword_id: int, name: str, description: str = "") -> int:
        """更新关键词"""
        query = """
        UPDATE keywords
        SET name = %s, description = %s
        WHERE id = %s
        """
        return self.db.execute_update(query, (name, description, keyword_id))
    
    def delete_keyword(self, keyword_id: int) -> int:
        """删除关键词"""
        query = "DELETE FROM keywords WHERE id = %s"
        return self.db.execute_update(query, (keyword_id,))
    
    def get_keyword_by_id(self, keyword_id: int) -> Optional[Dict]:
        """根据ID获取关键词"""
        query = "SELECT * FROM keywords WHERE id = %s"
        results = self.db.execute_query(query, (keyword_id,))
        return results[0] if results else None
    
    def get_keyword_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取关键词"""
        query = "SELECT * FROM keywords WHERE name = %s"
        results = self.db.execute_query(query, (name,))
        return results[0] if results else None
    
    def get_all_keywords(self) -> List[Dict]:
        """获取所有关键词"""
        query = "SELECT * FROM keywords ORDER BY name"
        return self.db.execute_query(query)
    
    def link_paper_to_keyword(self, paper_id: int, keyword_id: int) -> int:
        """将论文与关键词关联"""
        query = """
        INSERT INTO paper_keywords (paper_id, keyword_id)
        VALUES (%s, %s)
        """
        return self.db.execute_insert(query, (paper_id, keyword_id))
    
    def unlink_paper_from_keyword(self, paper_id: int, keyword_id: int) -> int:
        """解除论文与关键词的关联"""
        query = """
        DELETE FROM paper_keywords
        WHERE paper_id = %s AND keyword_id = %s
        """
        return self.db.execute_update(query, (paper_id, keyword_id))
    
    def get_keywords_for_paper(self, paper_id: int) -> List[Dict]:
        """获取论文的所有关键词"""
        query = """
        SELECT k.* FROM keywords k
        JOIN paper_keywords pk ON k.id = pk.keyword_id
        WHERE pk.paper_id = %s
        """
        return self.db.execute_query(query, (paper_id,))


class UserRepository:
    """用户数据仓库，提供用户相关的数据库操作"""
    
    def __init__(self, db_manager: DatabaseManager):
        """初始化用户仓库"""
        self.db = db_manager
    
    def add_user(self, username: str, email: str, password_hash: str) -> int:
        """添加用户"""
        query = """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
        """
        return self.db.execute_insert(query, (username, email, password_hash))
    
    def update_user(self, user_id: int, username: str = None, email: str = None, password_hash: str = None) -> int:
        """更新用户信息"""
        # 获取当前用户信息
        current_user = self.get_user_by_id(user_id)
        if not current_user:
            return 0
        
        # 使用当前值或新值
        username = username or current_user['username']
        email = email or current_user['email']
        password_hash = password_hash or current_user['password_hash']
        
        query = """
        UPDATE users
        SET username = %s, email = %s, password_hash = %s
        WHERE id = %s
        """
        return self.db.execute_update(query, (username, email, password_hash, user_id))
    
    def delete_user(self, user_id: int) -> int:
        """删除用户"""
        query = "DELETE FROM users WHERE id = %s"
        return self.db.execute_update(query, (user_id,))
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE id = %s"
        results = self.db.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = %s"
        results = self.db.execute_query(query, (username,))
        return results[0] if results else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """根据邮箱获取用户"""
        query = "SELECT * FROM users WHERE email = %s"
        results = self.db.execute_query(query, (email,))
        return results[0] if results else None
    
    def add_favorite(self, user_id: int, paper_id: int) -> int:
        """添加收藏"""
        query = """
        INSERT INTO user_favorites (user_id, paper_id)
        VALUES (%s, %s)
        """
        return self.db.execute_insert(query, (user_id, paper_id))
    
    def remove_favorite(self, user_id: int, paper_id: int) -> int:
        """移除收藏"""
        query = """
        DELETE FROM user_favorites
        WHERE user_id = %s AND paper_id = %s
        """
        return self.db.execute_update(query, (user_id, paper_id))
    
    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """获取用户收藏的论文"""
        query = """
        SELECT p.* FROM papers p
        JOIN user_favorites uf ON p.id = uf.paper_id
        WHERE uf.user_id = %s
        ORDER BY uf.created_at DESC
        """
        return self.db.execute_query(query, (user_id,))
    
    def follow_keyword(self, user_id: int, keyword_id: int) -> int:
        """关注关键词"""
        query = """
        INSERT INTO user_keywords (user_id, keyword_id)
        VALUES (%s, %s)
        """
        return self.db.execute_insert(query, (user_id, keyword_id))
    
    def unfollow_keyword(self, user_id: int, keyword_id: int) -> int:
        """取消关注关键词"""
        query = """
        DELETE FROM user_keywords
        WHERE user_id = %s AND keyword_id = %s
        """
        return self.db.execute_update(query, (user_id, keyword_id))
    
    def get_user_keywords(self, user_id: int) -> List[Dict]:
        """获取用户关注的关键词"""
        query = """
        SELECT k.* FROM keywords k
        JOIN user_keywords uk ON k.id = uk.keyword_id
        WHERE uk.user_id = %s
        """
        return self.db.execute_query(query, (user_id,))


# 测试函数
def test_database_connection():
    """测试数据库连接"""
    db = DatabaseManager()
    try:
        result = db.execute_query("SELECT 1")
        print("数据库连接测试成功:", result)
        return True
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False
    finally:
        db.close()


def test_paper_operations():
    """测试论文操作"""
    db = DatabaseManager()
    paper_repo = PaperRepository(db)
    
    # 添加测试论文
    test_paper = {
        'title': 'Test Paper Title',
        'abstract': 'This is a test abstract for the paper.',
        'authors': ['Author One', 'Author Two'],
        'link': 'http://arxiv.org/abs/test123',
        'comment': 'Test comment',
        'date': '2025-05-05',
        'arxiv_id': 'test123'
    }
    
    try:
        # 添加论文
        paper_id = paper_repo.add_paper(test_paper)
        print(f"添加论文成功，ID: {paper_id}")
        
        # 获取论文
        paper = paper_repo.get_paper_by_id(paper_id)
        print(f"获取论文成功: {paper['title']}")
        
        # 更新论文
        test_paper['title'] = 'Updated Test Paper Title'
        paper_repo.update_paper(paper_id, test_paper)
        updated_paper = paper_repo.get_paper_by_id(paper_id)
        print(f"更新论文成功: {updated_paper['title']}")
        
        # 删除论文
        paper_repo.delete_paper(paper_id)
        deleted_paper = paper_repo.get_paper_by_id(paper_id)
        print(f"删除论文成功: {deleted_paper is None}")
        
        return True
    except Exception as e:
        print(f"论文操作测试失败: {e}")
        return False
    finally:
        db.close()


def test_keyword_operations():
    """测试关键词操作"""
    db = DatabaseManager()
    keyword_repo = KeywordRepository(db)
    
    try:
        # 添加关键词
        keyword_id = keyword_repo.add_keyword("Test Keyword", "This is a test keyword")
        print(f"添加关键词成功，ID: {keyword_id}")
        
        # 获取关键词
        keyword = keyword_repo.get_keyword_by_id(keyword_id)
        print(f"获取关键词成功: {keyword['name']}")
        
        # 更新关键词
        keyword_repo.update_keyword(keyword_id, "Updated Test Keyword", "This is an updated test keyword")
        updated_keyword = keyword_repo.get_keyword_by_id(keyword_id)
        print(f"更新关键词成功: {updated_keyword['name']}")
        
        # 获取所有关键词
        all_keywords = keyword_repo.get_all_keywords()
        print(f"获取所有关键词成功，数量: {len(all_keywords)}")
        
        # 删除关键词
        keyword_repo.delete_keyword(keyword_id)
        deleted_keyword = keyword_repo.get_keyword_by_id(keyword_id)
        print(f"删除关键词成功: {deleted_keyword is None}")
        
        return True
    except Exception as e:
        print(f"关键词操作测试失败: {e}")
        return False
    finally:
        db.close()


def test_user_operations():
    """测试用户操作"""
    db = DatabaseManager()
    user_repo = UserRepository(db)
    
    try:
        # 添加用户
        user_id = user_repo.add_user("testuser", "test@example.com", "hashed_password")
        print(f"添加用户成功，ID: {user_id}")
        
        # 获取用户
        user = user_repo.get_user_by_id(user_id)
        print(f"获取用户成功: {user['username']}")
        
        # 更新用户
        user_repo.update_user(user_id, username="updateduser")
        updated_user = user_repo.get_user_by_id(user_id)
        print(f"更新用户成功: {updated_user['username']}")
        
        # 删除用户
        user_repo.delete_user(user_id)
        deleted_user = user_repo.get_user_by_id(user_id)
        print(f"删除用户成功: {deleted_user is None}")
        
        return True
    except Exception as e:
        print(f"用户操作测试失败: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("开始测试数据库操作...")
    
    # 测试数据库连接
    if not test_database_connection():
        print("数据库连接测试失败，退出测试")
        sys.exit(1)
    
    # 测试论文操作
    test_paper_operations()
    
    # 测试关键词操作
    test_keyword_operations()
    
    # 测试用户操作
    test_user_operations()
    
    print("数据库操作测试完成")
