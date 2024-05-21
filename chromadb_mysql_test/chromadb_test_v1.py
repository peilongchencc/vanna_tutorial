"""
File path:/data/vanna/chromadb_test_v1.py
Author: peilongchencc@163.com
Description: 
Requirements: 
pip install chromadb
Time: 2024/05/15 20:07:57
Reference Link: 
Notes: 
"""
import os
from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from loguru import logger
from dotenv import load_dotenv

load_dotenv('env_config/.env.local')

# 设置日志
logger.remove()
logger.add("chromadb_test.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

api_key=os.getenv("OPENAI_API_KEY")

# vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})
vn = MyVanna(config={'api_key': api_key, 'model': 'gpt-4-turbo'})

vn.connect_to_mysql(host='localhost', dbname='irmdata', user='root', password='Flameaway3.', port=3306)

# 获取mysql中数据库(这里笔者使用的是自建的irmdata)的元数据(包括列名、字段数据类型、字段默认值、字段注释等。)(不是数据本身,如果想要获取数据本身需要使用 SELECT 语句)
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'irmdata'")
logger.info(f"df_info的结果为:\n{df_information_schema}")

plan = vn.get_training_plan_generic(df_information_schema)

logger.info(f"plan为:\n{plan},{type(plan)}")

plan_summary = plan.get_summary()
logger.info(f"plan_summary的结果为:\n{plan_summary}")

# If you like the plan, then uncomment this and run it to train
# 如果你喜欢这个计划，那就取消这行的注释并运行它以进行训练。
# 伪训练，其实就是将内容加入到向量数据库中。
vn.train(plan=plan)
logger.info(f"train后的vn为:\n{vn}")

# 打印训练数据
training_data = vn.get_training_data()
logger.info(f"训练数据为:\n{training_data}")

# 查询数据,但不进行绘图。
vn_rtn = vn.ask(question="请列出每所大学及其专业的名称、研究方向以及录取人数。", visualize=False)
logger.info(f"查询结果为:\n{vn_rtn}")