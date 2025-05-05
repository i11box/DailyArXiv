import pymysql
import toml

# 读取配置
config = toml.load('config.toml')

# 连接参数
conn_params = {
    'host': config['DB_HOST'],
    'port': config['DB_PORT'],
    'user': config['DB_USER'],
    'password': str(config['DB_PASSWORD']),  # 确保密码是字符串
    'database': config['DB_NAME'],
    'charset': 'utf8mb4'
}

try:
    print("尝试连接数据库，参数:", conn_params)
    connection = pymysql.connect(**conn_params)
    print("连接成功!")
    
    # 测试简单查询
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库中有 {len(tables)} 张表:")
        for table in tables:
            print(f"- {table[0]}")
    
    connection.close()
    print("连接已关闭")
    
except pymysql.Error as e:
    print(f"连接失败 - 错误代码: {e.args[0]}")
    print(f"错误信息: {e.args[1]}")
    
except Exception as e:
    print(f"未知错误: {type(e)} - {str(e)}")
