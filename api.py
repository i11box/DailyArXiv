import os
import json
import toml
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from db.db_repo import DatabaseRepository

app = Flask(__name__)
CORS(app)  # 启用跨域支持

db = DatabaseRepository()

@app.route('/api/papers/latest', methods=['GET'])
def get_latest_papers():
    """获取最近的论文，按关键词分类"""
    try:
        # 从数据库获取最近日期
        latest_date = db.paper_repo.get_latest_date()
        if not latest_date:
            return jsonify({"error": "没有找到论文数据"}), 404
            
        # 获取该日期的所有论文
        papers = db.paper_repo.get_papers_by_date(latest_date)
        
        # 按关键词分类
        papers_by_keyword = {}
        for paper in papers:
            keyword = paper.get('keyword', 'Uncategorized')
            if keyword not in papers_by_keyword:
                papers_by_keyword[keyword] = []
            papers_by_keyword[keyword].append(paper)
        
        return jsonify({
            "date": latest_date,
            "papers": papers_by_keyword
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    try:
        config = toml.load('config.toml')
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置信息"""
    try:
        data = request.json
        
        # 读取当前配置
        current_config = toml.load('config.toml')
        
        # 更新配置
        for key, value in data.items():
            current_config[key] = value
        
        # 写入配置文件
        with open('config.toml', 'w') as f:
            toml.dump(current_config, f)
        
        return jsonify({"message": "配置已更新", "config": current_config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    """获取关键词列表"""
    try:
        keywords = db.get_keywords()
        return jsonify(keywords)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
