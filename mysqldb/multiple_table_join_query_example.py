"""
File path:multiple_table_join_query_example.py
Author: peilongchencc@163.com
Description: mysql多表联合查询示例
Requirements: 
1. pip install python-dotenv aiomysql
2. 当前目录下创建 `.env.local` 文件,写入配置项
3. 准备好需要的sql脚本
Reference Link: 
Notes: 
aiomysql返回的数据格式由游标决定:
- `async with conn.cursor() as cur:` 返回的结果是元组。
    输出示例: (('北京工业大学', '数学', '应用数学', 12), ('北京工业大学', '数学', '基础数学', 12), ('北京工业大学', '物理', '应用物理', 11))
- `async with conn.cursor(aiomysql.DictCursor) as cur:` 返回的结果是字典。
    输出示例: [{'university_name': '北京工业大学', 'major': '数学', 'research_direction': '应用数学', 'num_of_major_admissions': 12}, {'university_name': '北京工业大学', 'major': '数学', 'research_direction': '基础数学', 'num_of_major_admissions': 12}, {'university_name': '北京工业大学', 'major': '物理', 'research_direction': '应用物理', 'num_of_major_admissions': 11}]
"""
import os
import time
import asyncio
import aiomysql
from dotenv import load_dotenv
load_dotenv('.env.local')

def read_file(file_path):
    """读取文件并将其作为一个字符串返回。
    Args:
        file_path(str):文件路径。
    Return:
        readed_result(str):读取的结果。
    Notes:
    `read()`函数会一次性读取整个文件内容，并将其作为一个字符串（对于文本文件）或字节串（对于二进制文件）返回。
    `readline()`函数从文件中一次读取一行内容，并返回字符串。
    `readlines()`函数一次性读取文件中所有行，并将其存储为列表，列表中的每个元素是文件的一行。
    """
    with open(file_path, "r") as file:
        readed_result = file.read()
    return readed_result

def current_timestamp():
    """返回当前日期时间的字符串表示形式,格式为: 2023-08-15 11:29:22 """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

async def create_mysql_pool():
    """基于aiomysql创建连接池
    """
    try:
        # 从环境变量中获取数据库连接信息
        mysql_db_host = os.getenv("MYSQL_DB_HOST")
        mysql_db_port = int(os.getenv("MYSQL_DB_PORT")) # 字符串要转int,端口号需要int类型
        mysql_db_user = os.getenv("MYSQL_DB_USER")
        mysql_db_password = os.getenv("MYSQL_DB_PASSWORD")
        mysql_db_name = os.getenv("MYSQL_DB_NAME")
        
        # 创建连接池
        mysql_pool = await aiomysql.create_pool(
            host=mysql_db_host,
            port=mysql_db_port,
            user=mysql_db_user,
            password=mysql_db_password,
            db=mysql_db_name,
            minsize=5,
            maxsize=10
        )
        return mysql_pool
    except Exception as e:
        print(f"Error occurred while creating MySQL pool: {e}")

async def execute_mysql_command(sql_sentence):
    """执行非查询的MySQL命令(如INSERT, UPDATE, CREATE)
    Args:
        sql_sentence(str): SQL语句。
    """
    try:
        # 从mysql连接池获取的连接
        mysql_pool = await create_mysql_pool()
        async with mysql_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql_sentence)
                await conn.commit()  # 确保执行了commit操作
    except Exception as e:
        print(f"Error occurred while executing MySQL command: {e}")
        # 如果执行出错，则回滚数据
        await conn.rollback()

async def fetch_data_from_mysql(sql_sentence):
    """从mysql中获取数据,以字典形式(DictCursor)返回每行数据。
    Args:
        sql_sentence(str): SQL查询语句,例如 "SELECT * FROM your_table;"。
    Return:
        fetch_result(list): 查询结果,格式为列表中每一项为字典。
    """
    try:
        # 从mysql连接池获取的连接
        mysql_pool = await create_mysql_pool()
        async with mysql_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:  # 使用DictCursor
                await cur.execute(sql_sentence)
                # 获取查询结果
                fetch_result = await cur.fetchall()
                return fetch_result
    except Exception as e:
        print(f"Error occurred while fetching data from MySQL: {e}")

async def main():
    # 读取sql文件为字符串
    table_admission = read_file("university_admission_information.sql")
    table_major = read_file("university_major_information.sql")

    # 执行sql语句
    await execute_mysql_command(table_admission)
    await execute_mysql_command(table_major)

    # 执行查询,联合这两个表查询每个专业的招生人数和研究方向。
    query = """
    SELECT a.university_name, a.major, m.research_direction, a.num_of_major_admissions
    FROM university_admission_information a
    JOIN university_major_information m ON a.university_name = m.university_name AND a.major = m.major;
    """
    data = await fetch_data_from_mysql(query)
    print(data)

if __name__ == "__main__":
    asyncio.run(main())