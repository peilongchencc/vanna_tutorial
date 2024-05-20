"""
Description: 该脚本连接到名为 'Chinook.sqlite' 的 SQLite 数据库，检索所有表名，并且对于每个表，打印该表的结构（即列信息）。

Notes: 
- 脚本使用 sqlite3 模块与 SQLite 数据库进行交互。
- 首先连接到数据库并创建一个 cursor 对象。
- 然后从数据库中检索所有表名。
- 对于每个表，检索并打印表的结构。
- 最后关闭与数据库的连接。
"""
import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('Chinook.sqlite')

# 创建一个cursor对象
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("数据库中的表有：")
for table in tables:
    print(table[0])

# 对于每个表，获取其结构
for table in tables:
    print(f"\n表 {table[0]} 的结构：")
    cursor.execute(f"PRAGMA table_info({table[0]});")
    columns = cursor.fetchall()
    for column in columns:
        print(column)

# 关闭连接
conn.close()
