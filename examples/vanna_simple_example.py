"""
Description: 测试通过openai的chat模型(同步)将bank77中的英文问句转为中文、与大模型交互。
Notes: 
因 "启明银行" 属于现实中不存在的银行，生成文本的效果不好，所以采用先定义为 "招商银行" 客服角色，再做替换。
"""
import sys
import os

# # 获取当前脚本的绝对路径
# current_script_path = os.path.abspath(__file__)
# # 获取当前脚本的父目录的父目录
# parent_directory_of_the_parent_directory = os.path.dirname(os.path.dirname(current_script_path))
# # 将这个目录添加到 sys.path
# sys.path.append(parent_directory_of_the_parent_directory)

import json
import random
from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv('env_config/.env.local')

# 设置日志
logger.remove()
logger.add("openai_stream.log", rotation="1 GB", backtrace=True, diagnose=True, format="{time} {level} {message}")

# 设置代理环境变量
os.environ['http_proxy'] = os.getenv("HTTP_PROXY")
os.environ['https_proxy'] = os.getenv("HTTPS_PROXY")

import vanna
from vanna.remote import VannaDefault
# vn = VannaDefault(model='chinook', api_key=vanna.get_api_key('my-email@example.com'))
vn = VannaDefault(model='chinook', api_key=vanna.get_api_key('peilongchencc@163.com'))  # 会提示输入发送到邮箱的验证码
vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
vn.ask("What are the top 10 albums by sales?")