# Chromadb Mysql

基于vanna利用chromadb(向量数据库)、MySQL生成SQL并用于查询。<br>

优势: 只需要了解表格结构，不接触表格中的具体数据信息。<br>

- [Chromadb Mysql](#chromadb-mysql)
  - [依赖项安装:](#依赖项安装)
  - [代码示例:](#代码示例)
  - [代码要点解析:](#代码要点解析)
    - [df\_information\_schema:](#df_information_schema)
    - [训练的关键-plan解析:](#训练的关键-plan解析)
    - [向量模型的使用:](#向量模型的使用)
    - [`ask(...)` 函数解析:](#ask-函数解析)
      - [generate\_sql模块:](#generate_sql模块)
    - [System Message](#system-message)
    - [User Message](#user-message)

## 依赖项安装:

```bash
pip install chromadb
```

## 代码示例:

```python
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
vn.train(plan=plan)
```

## 代码要点解析:

### df_information_schema:

`df_information_schema` 的结果类似如下内容:<br>

```log
   TABLE_CATALOG TABLE_SCHEMA                        TABLE_NAME  ... COLUMN_COMMENT  GENERATION_EXPRESSION SRS_ID
0            def      irmdata  university_admission_information  ...                                         None
1            def      irmdata  university_admission_information  ...           大学名称                          None
2            def      irmdata  university_admission_information  ...           专业名称                          None
3            def      irmdata  university_admission_information  ...         专业招生人数                          None
4            def      irmdata  university_admission_information  ...           创建时间                          None
5            def      irmdata  university_admission_information  ...           修改时间                          None
6            def      irmdata      university_major_information  ...                                         None
7            def      irmdata      university_major_information  ...           大学名称                          None
8            def      irmdata      university_major_information  ...           专业名称                          None
9            def      irmdata      university_major_information  ...           研究方向                          None
10           def      irmdata      university_major_information  ...           创建时间                          None
11           def      irmdata      university_major_information  ...           修改时间                          None

[12 rows x 22 columns]
```

### 训练的关键-plan解析:

经过 `vn.get_training_plan_generic(df_information_schema)` 得到的 `plan` 是一个类:<br>

```log
<class 'vanna.types.TrainingPlan'>
```

`plan.get_summary()`得到的结果依旧不是能看懂的:<br>

```log
['Train on Information Schema: def.irmdata university_admission_information', 'Train on Information Schema: def.irmdata university_major_information']
```

类中信息部分必须经过debug才能看到，其实是不同表的结构(依旧是元数据、不含具体数据):<br>

```markdown
这是`university_admission_information`表的信息，整理后如下：

- **表目录**：def
- **表架构**：irmdata
- **表名**：university_admission_information

| 列序号 | 列名                    | 数据类型   | 注释          |
|------|-----------------------|----------|-------------|
| 0    | id                    | int      |             |
| 1    | university_name       | varchar  | 大学名称       |
| 2    | major                 | varchar  | 专业名称       |
| 3    | num_of_major_admissions | int      | 专业招生人数     |
| 4    | create_time           | timestamp| 创建时间       |
| 5    | update_time           | timestamp| 修改时间       |

以上表格提供了每列的名称、数据类型和注释（如果有的话）。这样的格式使得信息更清晰，方便查看。
```

```markdown
这是`university_major_information`表的信息，整理后如下：

- **表目录**：def
- **表架构**：irmdata
- **表名**：university_major_information

| 列序号 | 列名                | 数据类型   | 注释          |
|------|-------------------|----------|-------------|
| 6    | id                | int      |             |
| 7    | university_name   | varchar  | 大学名称       |
| 8    | major             | varchar  | 专业名称       |
| 9    | research_direction| varchar  | 研究方向       |
| 10   | create_time       | timestamp| 创建时间       |
| 11   | update_time       | timestamp| 修改时间       |

以上表格提供了每列的名称、数据类型和注释（如果有的话）。这样的格式使得信息更清晰，方便查看。
```

### 向量模型的使用:

运行 `vn.train(plan=plan)` 后，终端会出现以下信息:<br>

```log
(langchain) root@iZ2zea5v77oawjy2qz7c20Z:/data/vanna# python chromadb_test_v1.py 
/root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz: 100%|█████████████████████████████████████████████| 79.3M/79.3M [22:44<00:00, 61.0kiB/s]
```

这是因为使用了 `vanna` 中的 `ChromaDB_VectorStore` 模块，其中`src/vanna/chromadb/chromadb_vector.py` 文件中的代码如下:<br>

```python
default_ef = embedding_functions.DefaultEmbeddingFunction()

class ChromaDB_VectorStore(VannaBase):
    def __init__(self, config=None):
        VannaBase.__init__(self, config=config)
        if config is None:
            config = {}

        path = config.get("path", ".")
        self.embedding_function = config.get("embedding_function", default_ef)  # 使用该模型进行向量化。
```

执行跳转:<br>

```python
class ONNXMiniLM_L6_V2(EmbeddingFunction[Documents]):
    MODEL_NAME = "all-MiniLM-L6-v2"
    DOWNLOAD_PATH = Path.home() / ".cache" / "chroma" / "onnx_models" / MODEL_NAME
    EXTRACTED_FOLDER_NAME = "onnx"
    ARCHIVE_FILENAME = "onnx.tar.gz"
    MODEL_DOWNLOAD_URL = (
        "https://chroma-onnx-models.s3.amazonaws.com/all-MiniLM-L6-v2/onnx.tar.gz"
    )
    _MODEL_SHA256 = "913d7300ceae3b2dbc2c50d1de4baacab4be7b9380491c27fab7418616a16ec3"

    # https://github.com/python/mypy/issues/7291 mypy makes you type the constructor if
    # no args
    def __init__(self, preferred_providers: Optional[List[str]] = None) -> None:
        ...
```

此时会发现，`all-MiniLM-L6-v2` 是 vanna 中 chromadb 使用的向量化模型。(生成的向量维度为384)<br>

> 不是你指定了 openai 就使用 openai 的 embedding 模型，这一点挺让人无语的。

### `ask(...)` 函数解析:

源码摘录:<br>

```python
    def ask(
        self,
        question: Union[str, None] = None,
        print_results: bool = True,
        auto_train: bool = True,
        visualize: bool = True,  # if False, will not generate plotly code
    ) -> Union[
        Tuple[
            Union[str, None],
            Union[pd.DataFrame, None],
            Union[plotly.graph_objs.Figure, None],
        ],
        None,
    ]:
        """
        **Example:**
        ```python
        vn.ask("What are the top 10 customers by sales?")
        ```

        Ask Vanna.AI a question and get the SQL query that answers it.

        Args:
            question (str): The question to ask.
            print_results (bool): Whether to print the results of the SQL query.
            auto_train (bool): Whether to automatically train Vanna.AI on the question and SQL query.
            visualize (bool): Whether to generate plotly code and display the plotly figure.

        Returns:
            Tuple[str, pd.DataFrame, plotly.graph_objs.Figure]: The SQL query, the results of the SQL query, and the plotly figure.
        """
```

#### generate_sql模块:

生成sql的关键是下列路径中的 `generate_sql` 函数。<br>

```bash
/root/anaconda3/envs/langchain/lib/python3.10/site-packages/vanna/base/base.py
```

`gennerate_sql`中的关键是下列代码:<br>

```python
prompt = self.get_sql_prompt(
    initial_prompt=initial_prompt,
    question=question,
    question_sql_list=question_sql_list,
    ddl_list=ddl_list,
    doc_list=doc_list,
    **kwargs,
)
```

内部Example如下:<br>

```python
vn.get_sql_prompt(
    question="What are the top 10 customers by sales?",
    question_sql_list=[{"question": "What are the top 10 customers by sales?", "sql": "SELECT * FROM customers ORDER BY sales DESC LIMIT 10"}],
    ddl_list=["CREATE TABLE customers (id INT, name TEXT, sales DECIMAL)"],
    doc_list=["The customers table contains information about customers and their sales."],
)
```

一般获取的表格结构就是 `doc_list` (不是CREATE语句)。<br>

This method is used to generate a prompt for the LLM to generate SQL.

Args:
    question (str): The question to generate SQL for.
    question_sql_list (list): A list of questions and their corresponding SQL statements.
    ddl_list (list): A list of DDL statements.
    doc_list (list): A list of documentation.

Returns:
    any: The prompt for the LLM to generate SQL.

`debug` 后看到的完整prompt如下:<br>

```log
"You are a SQL expert. \n===Additional Context \n\nThe following columns are in the university_admission_information table in the def database:\n\n|    | TABLE_CATALOG   | TABLE_SCHEMA   | TABLE_NAME                       | COLUMN_NAME             | DATA_TYPE   | COLUMN_COMMENT   |\n|---:|:----------------|:---------------|:---------------------------------|:------------------------|:------------|:-----------------|\n|  0 | def             | irmdata        | university_admission_information | id                      | int         |                  |\n|  1 | def             | irmdata        | university_admission_information | university_name         | varchar     | 大学名称             |\n|  2 | def             | irmdata        | university_admission_information | major                   | varchar     | 专业名称             |\n|  3 | def             | irmdata        | university_admission_information | num_of_major_admissions | int         | 专业招生人数           |\n|  4 | def             | irmdata        | university_admission_information | create_time             | timestamp   | 创建时间             |\n|  5 | def             | irmdata        | university_admission_information | update_time             | timestamp   | 修改时间             |\n\nThe following columns are in the university_major_information table in the def database:\n\n|    | TABLE_CATALOG   | TABLE_SCHEMA   | TABLE_NAME                   | COLUMN_NAME        | DATA_TYPE   | COLUMN_COMMENT   |\n|---:|:----------------|:---------------|:-----------------------------|:-------------------|:------------|:-----------------|\n|  6 | def             | irmdata        | university_major_information | id                 | int         |                  |\n|  7 | def             | irmdata        | university_major_information | university_name    | varchar     | 大学名称             |\n|  8 | def             | irmdata        | university_major_information | major              | varchar     | 专业名称             |\n|  9 | def             | irmdata        | university_major_information | research_direction | varchar     | 研究方向             |\n| 10 | def             | irmdata        | university_major_information | create_time        | timestamp   | 创建时间             |\n| 11 | def             | irmdata        | university_major_information | update_time        | timestamp   | 修改时间             |\n\n===Response Guidelines \n1. If the provided context is sufficient, please generate a valid SQL query without any explanations for the question. \n2. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql \n3. If the provided context is insufficient, please explain why it can't be generated. \n4. Please use the most relevant table(s). \n5. If the question has been asked and answered before, please repeat the answer exactly as it was given before. \n"
```

`message_log` 是与大模型交互的变量，效果如下:<br>

```python
message_log = [{'role': 'system', 'content': "You are a SQL expert. \n===Additional Context \n\nThe following columns are in the university_admission_information table in the def database:\n\n|    | TABLE_CATALOG   | TABLE_SCHEMA   | TABLE_NAME                       | COLUMN_NAME             | DATA_TYPE   | COLUMN_COMMENT   |\n|---:|:----------------|:---------------|:---------------------------------|:------------------------|:------------|:-----------------|\n|  0 | def             | irmdata        | university_admission_information | id                      | int         |                  |\n|  1 | def             | irmdata        | university_admission_information | university_name         | varchar     | 大学名称             |\n|  2 | def             | irmdata        | university_admission_information | major                   | varchar     | 专业名称             |\n|  3 | def             | irmdata        | university_admission_information | num_of_major_admissions | int         | 专业招生人数           |\n|  4 | def             | irmdata        | university_admission_information | create_time             | timestamp   | 创建时间             |\n|  5 | def             | irmdata        | university_admission_information | update_time             | timestamp   | 修改时间             |\n\nThe following columns are in the university_major_information table in the def database:\n\n|    | TABLE_CATALOG   | TABLE_SCHEMA   | TABLE_NAME                   | COLUMN_NAME        | DATA_TYPE   | COLUMN_COMMENT   |\n|---:|:----------------|:---------------|:-----------------------------|:-------------------|:------------|:-----------------|\n|  6 | def             | irmdata        | university_major_information | id                 | int         |                  |\n|  7 | def             | irmdata        | university_major_information | university_name    | varchar     | 大学名称             |\n|  8 | def             | irmdata        | university_major_information | major              | varchar     | 专业名称             |\n|  9 | def             | irmdata        | university_major_information | research_direction | varchar     | 研究方向             |\n| 10 | def             | irmdata        | university_major_information | create_time        | timestamp   | 创建时间             |\n| 11 | def             | irmdata        | university_major_information | update_time        | timestamp   | 修改时间             |\n\n===Response Guidelines \n1. If the provided context is sufficient, please generate a valid SQL query without any explanations for the question. \n2. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql \n3. If the provided context is insufficient, please explain why it can't be generated. \n4. Please use the most relevant table(s). \n5. If the question has been asked and answered before, please repeat the answer exactly as it was given before. \n"}, {'role': 'user', 'content': '请列出每所大学及其专业的名称、研究方向以及录取人数。'}]
```

如果转化为易于观察形式，效果如下:<br>

Here's the content in an easy-to-observe format:

---

### System Message

**Role:** system  
**Content:**

```log
You are a SQL expert. 
===Additional Context 

The following columns are in the university_admission_information table in the def database:

|    | TABLE_CATALOG   | TABLE_SCHEMA   | TABLE_NAME                       | COLUMN_NAME             | DATA_TYPE   | COLUMN_COMMENT   |
|---:|:----------------|:---------------|:---------------------------------|:------------------------|:------------|:-----------------|
|  0 | def             | irmdata        | university_admission_information | id                      | int         |                  |
|  1 | def             | irmdata        | university_admission_information | university_name         | varchar     | 大学名称             |
|  2 | def             | irmdata        | university_admission_information | major                   | varchar     | 专业名称             |
|  3 | def             | irmdata        | university_admission_information | num_of_major_admissions | int         | 专业招生人数           |
|  4 | def             | irmdata        | university_admission_information | create_time             | timestamp   | 创建时间             |
|  5 | def             | irmdata        | university_admission_information | update_time             | timestamp   | 修改时间             |

The following columns are in the university_major_information table in the def database:

|    | TABLE_CATALOG   | TABLE_SCHEMA   | TABLE_NAME                   | COLUMN_NAME        | DATA_TYPE   | COLUMN_COMMENT   |
|---:|:----------------|:---------------|:-----------------------------|:-------------------|:------------|:-----------------|
|  6 | def             | irmdata        | university_major_information | id                 | int         |                  |
|  7 | def             | irmdata        | university_major_information | university_name    | varchar     | 大学名称             |
|  8 | def             | irmdata        | university_major_information | major              | varchar     | 专业名称             |
|  9 | def             | irmdata        | university_major_information | research_direction | varchar     | 研究方向             |
| 10 | def             | irmdata        | university_major_information | create_time        | timestamp   | 创建时间             |
| 11 | def             | irmdata        | university_major_information | update_time        | timestamp   | 修改时间             |

===Response Guidelines 
1. If the provided context is sufficient, please generate a valid SQL query without any explanations for the question. 
2. If the provided context is almost sufficient but requires knowledge of a specific string in a particular column, please generate an intermediate SQL query to find the distinct strings in that column. Prepend the query with a comment saying intermediate_sql 
3. If the provided context is insufficient, please explain why it can't be generated. 
4. Please use the most relevant table(s). 
5. If the question has been asked and answered before, please repeat the answer exactly as it was given before.
```

### User Message

**Role:** user  
**Content:**

```log
请列出每所大学及其专业的名称、研究方向以及录取人数。
```

---

现在就可以执行 `llm_response = self.submit_prompt(prompt, **kwargs)` 部分了。<br>

```python
elif self.config is not None and "model" in self.config:
    print(
        f"Using model {self.config['model']} for {num_tokens} tokens (approx)"
    )
    response = self.client.chat.completions.create(
        model=self.config["model"],
        messages=prompt,
        max_tokens=self.max_tokens,
        stop=None,
        temperature=self.temperature,
    )
```

可以看到，使用的正是常规chat模型。`llm_response` 返回的结果如下:<br>

```sql
SELECT a.university_name, a.major, b.research_direction, a.num_of_major_admissions
FROM irmdata.university_admission_information a
JOIN irmdata.university_major_information b
ON a.university_name = b.university_name AND a.major = b.major;
```


