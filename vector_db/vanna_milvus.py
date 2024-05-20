"""
Description: 测试vanna使用自己的向量库。
Notes: 
"""

import os
import pandas as pd

from vanna.openai import OpenAI_Chat
from vanna.base import VannaBase

from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from pymilvus.client.types import LoadState

from vector_db.milvus_db import Milvuser
from env_config.milvus_config import bank_collection_config

from loguru import logger
from dotenv import load_dotenv

load_dotenv('env_config/.env.local')

mvs = Milvuser()

class MyCustomVectorDB(VannaBase):
    def __init__(self):
        """建立milvus连接(milvus默认为连接池形式)
        Ps: milvus的连接不需要返回值
        """
        connections.connect(host = os.getenv('MILVUS_DB_HOST'), port = os.getenv('MILVUS_DB_PORT'))
        # 获取或创建集合
        bank_collection = mvs.get_or_create_collection(bank_collection_config)
        
    def add_ddl(self, ddl: str, **kwargs) -> str:
        pass

    def add_documentation(self, doc: str, **kwargs) -> str:
        pass

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        pass

    def get_related_ddl(self, question: str, **kwargs) -> list:
        pass

    def get_related_documentation(self, question: str, **kwargs) -> list:
        pass

    def get_similar_question_sql(self, question: str, **kwargs) -> list:
        pass

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        pass

    def remove_training_data(id: str, **kwargs) -> bool:
        pass


class MyVanna(MyCustomVectorDB, OpenAI_Chat):
    def __init__(self, config=None):
        MyCustomVectorDB.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})
