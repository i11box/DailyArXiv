import toml
from db.db_ops import DatabaseManager, PaperRepository

class DatabaseRepository:
    def __init__(self):
        """初始化数据库连接"""
        self.db = DatabaseManager()
        self.paper_repo = PaperRepository(self.db)

    def get_keywords(self):
        """
        从config.toml获取关键词列表
        如果读取失败，返回默认关键词
        """
        try:
            config = toml.load('config.toml')
            keywords = config.get('keywords', ["Time Series", "Trajectory", "Graph Neural Networks"])
            
            # 确保返回的是列表
            if not isinstance(keywords, list):
                keywords = ["Time Series", "Trajectory", "Graph Neural Networks"]
                print("警告：配置中的keywords不是列表格式，使用默认关键词")
                
            return keywords
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return ["Time Series", "Trajectory", "Graph Neural Networks"]
    
    def save_papers(self, papers):
        '''
        传入papers是一个dict, 键为keyword, 值为papers
        '''
        for keyword in papers.keys():
            for paper in papers[keyword]:  # 修正遍历逻辑
                # 处理日期格式 - 将ISO格式转换为MySQL兼容的日期格式
                date_str = paper.get('Date', '')
                if date_str and 'T' in date_str:
                    # 提取日期部分 (YYYY-MM-DD)
                    date_str = date_str.split('T')[0]
                
                # 获取Link字段，如果不存在则提供空字符串
                link = paper.get('Link', '')
                
                paper_data = {
                    'title': paper.get('Title', ''),
                    'abstract': paper.get('Abstract', ''),
                    'link': link,  # 添加link字段
                    'comment': paper.get('Comment', ''),
                    'date': date_str,
                    'keyword': keyword  # 添加keyword字段，保存关键词信息
                }
                
                try:
                    self.paper_repo.add_paper(paper_data)
                except Exception as e:
                    print(f"保存论文失败: {e}")
                    continue
    
    def close(self):
        self.db.close()
