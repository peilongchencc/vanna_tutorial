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
import pandas as pd

load_dotenv('env_config/.env.local')

# 设置日志
logger.remove()
logger.add("chromadb_test.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

def log_dataframe(df, filename):
    """为避免省略号的解决措施
    """
    # 确保 logs 目录存在
    os.makedirs('logs', exist_ok=True)
    # 将DataFrame保存为CSV文件
    path = f"./logs/{filename}"
    df.to_csv(path, index=False)
    # 在日志中记录文件位置
    logger.info(f"DataFrame已保存至{path}")

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

api_key=os.getenv("OPENAI_API_KEY")

# vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})
vn = MyVanna(config={'api_key': api_key, 'model': 'gpt-4-turbo'})

vn.connect_to_mysql(host='localhost', dbname='irmdata', user='root', password='Flameaway3.', port=3306)

# # 如果存在过时或错误的信息，您可以删除训练数据。
# # vn.remove_training_data(id='acb8f129-3be0-5645-85b1-a587a02fa059-sql')
# vn.remove_training_data(id='37e13bcc-6056-5b69-af66-c3bd89ff56a9-doc')
# vn.remove_training_data(id='5c911e10-0b50-5f62-8153-3da86ff8260d-doc')

# # # 打印训练数据
# training_data = vn.get_training_data()
# # logger.info(f"训练数据为:\n{training_data}")
# log_dataframe(training_data, "training_data_2.csv")

# 获取mysql中数据库(这里笔者使用的是自建的irmdata)的元数据(包括列名、字段数据类型、字段默认值、字段注释等。)(不是数据本身,如果想要获取数据本身需要使用 SELECT 语句)
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'irmdata'")
# logger.info(f"df_info的结果为:\n{df_information_schema}")
log_dataframe(df_information_schema, "df_information_schema.csv")

plan = vn.get_training_plan_generic(df_information_schema)
logger.info(f"plan为:\n{plan},{type(plan)}")

plan_summary = plan.get_summary()
logger.info(f"plan_summary的结果为:\n{plan_summary}")

# If you like the plan, then uncomment this and run it to train
# 如果你喜欢这个计划，那就取消这行的注释并运行它以进行训练。
vn.train(plan=plan)
logger.info(f"train后的vn为:\n{vn}")

# 打印训练数据
training_data = vn.get_training_data()
# logger.info(f"训练数据为:\n{training_data}")
log_dataframe(training_data, "training_data_new.csv")

vn_rtn = vn.ask(question="请列出每所大学及其专业的名称、研究方向以及录取人数。")
logger.info(f"查询结果为:\n{vn_rtn}")