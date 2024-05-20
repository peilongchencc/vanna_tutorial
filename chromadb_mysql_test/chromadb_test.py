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

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})

vn.connect_to_mysql(host='localhome', dbname='irmdata', user='root', password='Flameaway3.', port=3306)

# The information schema query may need some tweaking depending on your database. This is a good starting point.
# df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")  # 查看所有数据库的信息,但因为上面指定了数据库，所以只会查询相关的内容。
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'irmdata'")


# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = vn.get_training_plan_generic(df_information_schema)
logger.info(f"plan为:\n{plan}")

# If you like the plan, then uncomment this and run it to train
# vn.train(plan=plan)

# The following are methods for adding training data. Make sure you modify the examples to match your database.

# DDL statements are powerful because they specify table names, colume names, types, and potentially relationships
vn.train(ddl="""
    CREATE TABLE IF NOT EXISTS my-table (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        age INT
    )
""")

# Sometimes you may want to add documentation about your business terminology or definitions.
# 有时候，您可能需要添加有关您的业务术语或定义的文档。
vn.train(documentation="Our business defines OTIF score as the percentage of orders that are delivered on time and in full")

# You can also add SQL queries to your training data. This is useful if you have some queries already laying around. You can just copy and paste those from your editor to begin generating new SQL.
# 您还可以将SQL查询添加到您的训练数据中。如果您已经有一些现成的查询，这会很有用。您可以直接从编辑器中复制并粘贴这些查询，以开始生成新的SQL。
vn.train(sql="SELECT * FROM my-table WHERE name = 'John Doe'")

# At any time you can inspect what training data the package is able to reference
# 您可以随时检查package可以引用的训练数据。
training_data = vn.get_training_data()
logger.info(f"训练数据为:{training_data}")

# You can remove training data if there's obsolete/incorrect information. 
# 如果存在过时或错误的信息，您可以删除训练数据。
vn.remove_training_data(id='1-ddl')

vn.ask(question=...)