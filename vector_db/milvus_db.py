"""
Description: 实现向量数据库Milvus类的所有操作。
Notes: 
1. 在 pymilvus 中，数据插入操作默认是异步的。
2. 查询操作通常是同步的。这意味着当你执行一个查询操作，如使用 search 或 query 方法，程序会在查询完成并得到结果之前阻塞。查询操作返回结果后，你的代码才会继续执行。
这种同步执行方式使得在编写查询逻辑时代码更直接，因为你可以立即处理查询返回的结果，无需额外处理异步调用或状态检查。例如:

>>> results = collection.search(data, params)
>>> # 直接处理结果
>>> for result in results:
>>>     print(result)

"""
import os
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from pymilvus.client.types import LoadState
from dotenv import load_dotenv

# 以环境变量方式加载配置,正式运行时可将下列代码注释,只在脚本文件导入一次即可。
load_dotenv('env_config/.env.local')

class Milvuser():
    def __init__(self):
        """建立milvus连接(milvus默认为连接池形式)
        Ps: milvus的连接不需要返回值
        """
        connections.connect(host = os.getenv('MILVUS_DB_HOST'), port = os.getenv('MILVUS_DB_PORT'))
        
    def get_or_create_collection(self, collection_config):
        """获取或创建milvus集合
        Args:
            config(dict): 创建集合所需要的字典。
        Return:
            collection: 获取或创建的milvus集合
        Notes:
            建表时设置主键的auto_id=true,主键就由milvus来产生,所产生的主键数值确实是往上增的，但跟那种每次+1的递增不一样。
            因为自动产生的主键值是基于时间戳的,是一个很大的数字,每次insert都会用当前的时间戳来产生一批主键,同一批次里的主键是+1递增。但不同批次的主键的值有可能有间隔。
        """
        # 如果集合不存在就执行创建
        if not utility.has_collection(collection_config['collection_name']):
            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),    # 系统自增id,随机生成，非 0,1,2,3 形式
            ]
            for field in collection_config['fieldschema']:
                if field[1] == DataType.FLOAT_VECTOR:
                    # 设置向量字段
                    fields.append(FieldSchema(name=field[0], dtype=field[1], dim=field[2]))
                else:
                    # 设置其他字段
                    fields.append(FieldSchema(name=field[0], dtype=field[1], max_length=field[2]))

            # 创建集合架构
            schema = CollectionSchema(fields=fields, description=collection_config['description'])

            # 创建集合
            collection = Collection(name=collection_config['collection_name'], schema=schema)

            # 设置索引参数
            collection.create_index(field_name=collection_config['index_field_name'], index_params=collection_config['index_params'])
        # 如果集合存在,获取集合
        else:
            collection = Collection(collection_config['collection_name'])
        # 返回创建的集合对象
        return collection

    def delete_collection(self, collection_name):
        """根据milvus的集合名称删除集合
        Notes:
            执行了删除操作返回True,没有执行返回False,即milvus中还没有该集合。
        """
        # 如果集合存在，输出True；否则输出False。
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            return True
        else:
            return False

    def check_collection_list(self):
        """列出milvus中所有的集合
        """
        # 列出所有集合
        collections = utility.list_collections()
        return collections

    def check_collection_load_state(self, collection_name):
        """查看milvus中某集合的加载状态
        Notes:
            1. load_state的type为枚举类型(`enum`)。
            2. 状态分为 "Loaded"、"NotLoad"、"NotExist"、"Loading"
        """
        # 获取集合的内存加载状态
        load_state = utility.load_state(collection_name)
        if load_state == LoadState.Loaded:
            return  "Loaded"
        elif load_state == LoadState.NotLoad:
            return  "NotLoad"
        elif load_state == LoadState.Loading:
            return  "Loading"
        # 集合不存在时
        else:
            return "NotExist"

    def check_collection_entity_num(self, collection_name):
        """获取milvus集合中的实体数量
        Args:
            collection_name(str): milvus集合的名称,例如: 'standard_financial_question_collection'
        """
        # 如果集合存在，输出True；否则输出False。
        if utility.has_collection(collection_name):
            # 连接milvus集合
            milvus_collection = Collection(name=collection_name)
            num_entities = milvus_collection.num_entities
            # 可通过 f"\n{milvus_collection.name}集合中num_entities量级为: {num_entities}" 打印查看效果
            return num_entities
        else:
            return False
    
    def load_collection_to_memory(self, collection_name):
        """将集合加载到内存
        Notes:
            从内存检索的速度快于从硬盘检索,所以milvus需要将数据加载到内存。
        """
        # 如果集合存在，输出True；否则输出False。
        if utility.has_collection(collection_name):
            collection = Collection(collection_name)
            collection.load()

    def release_collection_from_memory(self, collection_name):
        """将集合从内存释放
        Notes:
            1. 在查询结束后,可以选择将集合从内存释放,减少内存占用。
            2. 无论集合是否已加载到内存,都可以执行 `release()`。
        """
        # 如果集合存在，输出True；否则输出False。
        if utility.has_collection(collection_name):
            collection = Collection(collection_name)
            collection.release()

    def insert_data(self, collection, data):
        """
        将文本和向量插入 Milvus 集合。
        Args:
            collection: Milvus 集合对象。
            data(list): 数据列表。
        Notes:
            1. data中每一项参数都是列表,Milvus是以列表形式插入数据的,
               例如要插入10条数据,那么text字段的列表中就有10条数据,同理source_from字段的列表中也有10条数据。
            2. 执行数据插入集合中,无返回值。
            3. Milvus不执行向量化操作,需要先将文本转为向量,然后执行向量插入操作。
            4. 插入顺序一定要与构建的collection顺序一致!!!
        """
        # 将数据插入到集合中
        collection.insert(data)
        print(f"现在进行数据刷新... ...")
        # 刷新数据
        collection.flush()
        print(f"现在进行数据刷新成功~")

    def search_data(self, search_config):
        """从milvus集合中查找相似text
        Args:
            search_config (dict): 搜索配置字典，包括以下键：
                - collection_name (str): milvus中集合名称
                - data_vec (list): 向量化数据
                - anns_field (str): 用于从集合中检索的向量字段名称
                - search_params (dict): 检索方式参数字典，包括以下键：
                    - metric_type (str): 距离度量类型
                    - top_K (int): 返回的最近邻居数量
                    - params (dict): 其他检索参数字典，包括以下键：
                        - radius (float): 检索半径
                        - range_filter (float): 范围过滤器
                - limit (int): 返回结果的数量限制
                - output_fields (list): 输出的字段列表
        Return:
            all_search_result (dict): 相似text组成的字典。
        """
        collection_name = search_config["collection_name"]
        data_vec = search_config["data_vec"]
        anns_field = search_config["anns_field"]
        search_params = search_config["search_params"]
        limit = search_config["limit"]
        output_fields = search_config["output_fields"]
        
        # 查看集合的内存加载状态,只有集合处于内存中才能进行检索。
        load_state = self.check_collection_load_state(collection_name)

        # 检查集合的加载状态,状态分为 "Loaded"、"NotLoad"、"NotExist"、"Loading"
        # 这里只区分加载/未加载两种状态。
        if load_state == "NotLoad":
            # 获取集合对象
            collection = Collection(collection_name)
            # 将集合加载到内存
            collection.load()
        else:
            # 获取集合对象
            collection = Collection(collection_name)

        # 构建search参数
        search_result = collection.search(data_vec, anns_field, search_params, limit=limit, output_fields=output_fields)

        # search_result是一个<class 'pymilvus.client.abstract.SearchResult'>类，但可像列表一样调用，查询结果在索引0。
        search_result_extract = search_result[0]
        # 将最终返回的结果放入一个字典
        all_search_result = {}
        for idx, item in enumerate(search_result_extract,1):
            each_res = item.__dict__    # 结果类似：{'id': 263663, 'distance': 1.0, 'fields': {'id': 263663, 'text': '老师'}}，类型为<class 'dict'>
            idx_name = f"结果{idx}"
            all_search_result[idx_name] = each_res

        return all_search_result

    def delete_data_according_expr(self, expression, collection_name):
        """根据表达式删除milvus数据
        Args:
            expression(str): 布尔表达式, 请使用 milvus 支持的布尔表达式,例如: expr = "text == '货币三佳是t+1到账吗'"
            milvus_collection_name(str): milvus集合的名称,例如: 'standard_financial_question_collection'
        Return:
            无返回值
        Notes:
            1. milvus只允许根据表达式删除数据。
            2. milvus不支持单独修改某条数据的某个字段。
            3. milvus更改数据其实是删除然后重新插入的操作。
        """
        # 获取集合对象
        milvus_collection = Collection(collection_name)
        # 传入Expression,使用布尔表达式删除数据
        milvus_collection.delete(expression)
        # 提交更改
        milvus_collection.load()

if __name__ == '__main__':
    # 配置集合字典
    bank_collection_config = {
        "collection_name": "bank_collection",
        "description": "search text",
        "fieldschema": [
            ["text", DataType.VARCHAR, 2000],
            ["source_from", DataType.VARCHAR, 2000],
            ["text_vector", DataType.FLOAT_VECTOR, 768]
            ],
        "index_params": {
            'metric_type': "COSINE",
            'index_type': "HNSW",
            'params': {'efConstruction': 10, 'M':60}
            },
        "index_field_name" : "text_vector"
    }

    # 文本的向量
    data_vec = []
    search_config = {
        "collection_name" : "bank_collection",
        # 检索用到的配置
        "search" :{
            # 文本的向量
            "data_vec" : data_vec,
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