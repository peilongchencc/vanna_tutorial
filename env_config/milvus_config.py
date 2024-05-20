"""
Description: 定义milvus集合创建、检索配置
Notes: 
"""

from pymilvus import DataType

# 配置集合字典
standard_collection_config = {
    "collection_name": "standard_collection",
    "description": "search text",
    "fieldschema": [
        ["question", DataType.VARCHAR, 2000],
        ["question_sql", DataType.VARCHAR, 2000],
        ["question_sql", DataType.VARCHAR, 2000],
        ["question_sql", DataType.VARCHAR, 2000],
        ["question_sql", DataType.VARCHAR, 2000],
        ["question_embed", DataType.FLOAT_VECTOR, 768]
        ],
    "index_params": {
        'metric_type': "COSINE",
        'index_type': "HNSW",
        'params': {'efConstruction': 10, 'M':60}
        },
    "index_field_name" : "text_vector"
}

# 搜索配置
search_config = {
    "collection_name" : "bank_collection",
    # 检索用到的配置
    "search" :{
        # 文本的向量,以`[]`占位,写入milvus时需要替换为真实文本向量
        "data_vec" : [],
        # 用于从集合中检索的向量字段名称
        "anns_field": "text_vector",
        # param即检索方式
        "search_params" : {
            "metric_type": 'COSINE',
            "top_K":50,
            "params": {
                # radius < distance <= range_filter，distance为相似度，milvus计算相似度时，如果完全相同，得到的结果可能是1.0000001192092896(有时是整整的 1.0)，所以，如果你想要返回相同数据，可以将"range_filter" : 1.0注释。
                "radius": 0,
                "range_filter" : 1.01
            }
        },
        "limit": 40,
        # 输出的字段
        "output_fields": ["id", "text", "source_from"]
    }
}