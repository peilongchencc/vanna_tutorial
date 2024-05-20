

| GitHub | PyPI | Documentation |
| ------ | ---- | ------------- |
| [![GitHub](https://img.shields.io/badge/GitHub-vanna-blue?logo=github)](https://github.com/vanna-ai/vanna) | [![PyPI](https://img.shields.io/pypi/v/vanna?logo=pypi)](https://pypi.org/project/vanna/) | [![Documentation](https://img.shields.io/badge/Documentation-vanna-blue?logo=read-the-docs)](https://vanna.ai/docs/) |

# Vanna tutorial
- [Vanna tutorial](#vanna-tutorial)
  - [How Vanna works](#how-vanna-works)
  - [User Interfaces](#user-interfaces)
  - [Getting started](#getting-started)
    - [Install](#install)
    - [Import](#import)
  - [Training](#training)
    - [Train with DDL Statements](#train-with-ddl-statements)
    - [Train with Documentation](#train-with-documentation)
    - [Train with SQL](#train-with-sql)
  - [Asking questions](#asking-questions)
  - [RAG vs. Fine-Tuning](#rag-vs-fine-tuning)
  - [Why Vanna?](#why-vanna)
  - [Why Vanna?(译文)](#why-vanna译文)
  - [Extending Vanna](#extending-vanna)
  - [Vanna in 100 Seconds](#vanna-in-100-seconds)
  - [More resources](#more-resources)

Vanna is an MIT-licensed open-source Python RAG (Retrieval-Augmented Generation) framework for SQL generation and related functionality.<br>

Vanna 是一个 MIT 许可的开源 Python RAG（检索增强生成）框架，**用于 SQL 生成和相关功能**。<br>

https://github.com/vanna-ai/vanna/assets/7146154/1901f47a-515d-4982-af50-f12761a3b2ce

![vanna-quadrants](https://github.com/vanna-ai/vanna/assets/7146154/1c7c88ba-c144-4ecf-a028-cf5ba7344ca2)

> any front end: 任何前端。


## How Vanna works

![Screen Recording 2024-01-24 at 11 21 37 AM](https://github.com/vanna-ai/vanna/assets/7146154/1d2718ad-12a8-4a76-afa2-c61754462f93)

> “DDL”指的是“数据定义语言”（Data Definition Language），这是用来定义或修改数据库结构的一组语法和命令。DDL 包括创建、修改、删除数据库中的表格、索引、约束等结构的命令，如 SQL 中的 CREATE、ALTER、DROP 等语句。

> plotly是一个用于创建交互式图表和数据可视化的Python库。

Vanna works in two easy steps - train a RAG "model" on your data.<br>

Vanna 通过两个简单步骤运作——在你的数据上训练一个 RAG“模型”。<br>

And then ask questions which will return SQL queries that can be set up to automatically run on your database.<br>

然后提出问题，这些问题将返回 SQL 查询，可以设置为自动在你的数据库上运行。<br>

1. **Train a RAG "model" on your data**.

2. **Ask questions**.

![](img/vanna-readme-diagram.png)

If you don't know what RAG is, don't worry -- you don't need to know how this works under the hood to use it.<br>

如果你不知道什么是 RAG，别担心 —— 你不需要知道它在底层是如何运作的就能使用它。<br>

You just need to know that you "train" a model, which stores some metadata and then use it to "ask" questions.<br>

你只需要知道你会"训练"一个模型，它会存储一些元数据，然后你可以用它来"提问"。<br>

See the [base class](https://github.com/vanna-ai/vanna/blob/main/src/vanna/base/base.py) for more details on how this works under the hood.

## User Interfaces
These are some of the user interfaces that we've built using Vanna. You can use these as-is or as a starting point for your own custom interface.

- [Jupyter Notebook](https://vanna.ai/docs/postgres-openai-vanna-vannadb/)
- [vanna-ai/vanna-streamlit](https://github.com/vanna-ai/vanna-streamlit)
- [vanna-ai/vanna-flask](https://github.com/vanna-ai/vanna-flask)
- [vanna-ai/vanna-slack](https://github.com/vanna-ai/vanna-slack)


## Getting started

See the [documentation](https://vanna.ai/docs/) for specifics on your desired database, LLM, etc.<br>

请查阅文档以获取有关您所需数据库、LLM等的具体信息。<br>

If you want to get a feel for how it works after training, you can try this [Colab notebook](https://vanna.ai/docs/app/)..<br>

如果您想在训练后了解它的工作方式，可以尝试这个Colab笔记本。<br>

### Install

```bash
pip install vanna
```

There are a number of optional packages that can be installed so see the [documentation](https://vanna.ai/docs/) for more details.<br>

有许多可选的软件包可供安装。因此，请参阅[文档](https://vanna.ai/docs/)以获取更多详细信息。<br>

### Import

See the [documentation](https://vanna.ai/docs/) if you're customizing the LLM or vector database.<br>

如果您正在定制LLM或向量数据库，请查看该文档。<br>

```python
# The import statement will vary depending on your LLM and vector database. This is an example for OpenAI + ChromaDB

from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': 'sk-...', 'model': 'gpt-4-...'})

# See the documentation for other options

```


## Training

You may or may not need to run these `vn.train` commands depending on your use case.<br>

根据您的具体应用场景，您可能需要或不需要运行这些 `vn.train` 命令。<br>

See the [documentation](https://vanna.ai/docs/) for more details.<br>

请查看[文档](https://vanna.ai/docs/)了解更多详情。<br>

These statements are shown to give you a feel for how it works.<br>

这些说明旨在让您了解其工作原理。<br>

### Train with DDL Statements

DDL statements contain information about the table names, columns, data types, and relationships in your database.<br>

DDL语句包含有关数据库中的表名、列、数据类型和关系的信息。<br>

```python
vn.train(ddl="""
    CREATE TABLE IF NOT EXISTS my-table (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        age INT
    )
""")
```

### Train with Documentation

Sometimes you may want to add documentation about your business terminology or definitions.<br>

有时候，您可能想要添加有关您的业务术语或定义的文档。<br>

```python
vn.train(documentation="Our business defines XYZ as ...")
```

### Train with SQL

You can also add SQL queries to your training data. This is useful if you have some queries already laying around.<br>

您也可以将SQL查询添加到您的训练数据中。这非常有用，如果您已经有一些现成的查询。<br>

You can just copy and paste those from your editor to begin generating new SQL.<br>

您可以直接从编辑器中复制并粘贴这些查询，开始生成新的SQL。<br>

```python
vn.train(sql="SELECT name, age FROM my-table WHERE name = 'John Doe'")
```


## Asking questions

```python
# 销售额前十的客户是哪些？
vn.ask("What are the top 10 customers by sales?")
```

You'll get SQL:<br>

```sql
SELECT c.c_name as customer_name,
        sum(l.l_extendedprice * (1 - l.l_discount)) as total_sales
FROM   snowflake_sample_data.tpch_sf1.lineitem l join snowflake_sample_data.tpch_sf1.orders o
        ON l.l_orderkey = o.o_orderkey join snowflake_sample_data.tpch_sf1.customer c
        ON o.o_custkey = c.c_custkey
GROUP BY customer_name
ORDER BY total_sales desc limit 10;
```

If you've connected to a database, you'll get the table:<br>

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>CUSTOMER_NAME</th>
      <th>TOTAL_SALES</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Customer#000143500</td>
      <td>6757566.0218</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Customer#000095257</td>
      <td>6294115.3340</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Customer#000087115</td>
      <td>6184649.5176</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Customer#000131113</td>
      <td>6080943.8305</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Customer#000134380</td>
      <td>6075141.9635</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Customer#000103834</td>
      <td>6059770.3232</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Customer#000069682</td>
      <td>6057779.0348</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Customer#000102022</td>
      <td>6039653.6335</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Customer#000098587</td>
      <td>6027021.5855</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Customer#000064660</td>
      <td>5905659.6159</td>
    </tr>
  </tbody>
</table>
</div>

You'll also get an automated Plotly chart:<br>

![](img/top-10-customers.png)


## RAG vs. Fine-Tuning

RAG
- Portable across LLMs
- Easy to remove training data if any of it becomes obsolete(过时的;废弃的)
- Much cheaper to run than fine-tuning
- More future-proof -- if a better LLM comes out, you can just swap it out

Fine-Tuning
- Good if you need to minimize tokens in the prompt
- Slow to get started
- Expensive to train and run (generally)

## Why Vanna?

1. **High accuracy on complex datasets.**
    - Vanna’s capabilities are tied to the training data you give it
    - More training data means better accuracy for large and complex datasets
2. **Secure and private.**
    - Your database contents(内容) are never sent to the LLM or the vector database
    - SQL execution happens in your local environment
3. **Self learning.**
    - If using via Jupyter, you can choose to "auto-train" it on the queries that were successfully executed
    - If using via other interfaces, you can have the interface prompt the user to provide feedback on the results
    - Correct question to SQL pairs are stored for future reference and make the future results more accurate
4. **Supports any SQL database.**
    - The package allows you to connect to any SQL database that you can otherwise connect to with Python
5. **Choose your front end.**
    - Most people start in a Jupyter Notebook.
    - Expose to your end users via Slackbot, web app, Streamlit app, or a custom front end.


## Why Vanna?(译文)

1. **在复杂数据集上具有高准确性。**
   - Vanna的性能取决于您提供的训练数据。
   - 更多的训练数据意味着在大型和复杂数据集上可以获得更好的准确性。

2. **安全且私密。**
   - 您的数据库内容永远不会发送到LLM或向量数据库。
   - SQL执行发生在您的本地环境中。

3. **自我学习。**
   - 如果通过Jupyter使用，您可以选择对成功执行的查询进行“自动训练”。
   - 如果通过其他界面使用，您可以让界面提示用户对结果提供反馈。
   - 正确的问题到SQL配对被存储以供将来参考，使未来的结果更加准确。

4. **支持任何SQL数据库。**
   - 该软件包允许您连接到任何您可以通过Python连接的SQL数据库。

5. **选择您的前端。**
   - 大多数人首先在Jupyter Notebook中开始。
   - 通过Slackbot、Web应用程序、Streamlit应用程序或自定义前端向您的最终用户展示。

## Extending Vanna

Vanna is designed to connect to any database, LLM, and vector database.<br>

Vanna旨在连接任何数据库、LLM和向量数据库。<br>

There's a [VannaBase](https://github.com/vanna-ai/vanna/blob/main/src/vanna/base/base.py) abstract base class that defines some basic functionality.<br>

[VannaBase](https://github.com/vanna-ai/vanna/blob/main/src/vanna/base/base.py) 是一个抽象基类，它定义了一些基本功能。<br>

The package provides implementations for use with OpenAI and ChromaDB.<br>

该软件包提供了用于OpenAI和ChromaDB的实现。<br>

You can easily extend Vanna to use your own LLM or vector database. See the [documentation](https://vanna.ai/docs/) for more details.<br>

您可以轻松扩展Vanna，使用您自己的LLM或向量数据库。更多详细信息请查看[文档](https://vanna.ai/docs/)。<br>


## Vanna in 100 Seconds

https://github.com/vanna-ai/vanna/assets/7146154/eb90ee1e-aa05-4740-891a-4fc10e611cab


## More resources
 - [Full Documentation](https://vanna.ai/docs/)
 - [Website](https://vanna.ai)
 - [Discord group for support](https://discord.gg/qUZYKHremx)
