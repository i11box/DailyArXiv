
import toml

from db.redis_queue import RedisQueue
from db.db_repo import DatabaseRepository
from workers import arxiv_worker
from workers.readme_writer import ReadmeWriter
from workers.arxiv_worker import ArxivWorker

db = DatabaseRepository()
rq = RedisQueue()
readme_writer = ReadmeWriter(db)
arxiv_worker = ArxivWorker(db, rq)

# 获取关键词
keywords = db.get_keywords() # get keywords

# Redis发布任务
rq.start_task(keywords)

# 启动爬虫
arxiv_worker.run_worker()

# 写README
readme_writer.write_readme(arxiv_worker.paper_keyword)

# 保存paper
arxiv_worker.save_papers()
db.close()
