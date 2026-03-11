"""
简化版股票监控脚本 - 适合GitHub Actions等云端环境
"""

import requests
import json
from datetime import datetime
import sys

# 监控的股票
STOCKS = {
    '600330': {'name': '天通股份', 'category': '上游'},
    '002222': {'name': '福晶科技', 'category': '上游'},
    '300620': {'name': '光库科技', 'category': '中游'},
    '301205': {'name': '联特科技', 'category': '中游'},
    '300502': {'name': '新易盛', 'category': '下游'},
    '000988': {'name': '华工科技', 'category': '下游'}
}

# 记录文件
LOG_FILE = 'stock_monitor.log'
ALERTS_FILE = 'alerts.json'

# 价格变化阈值
THRESHOLD = 3.0

# 记录上一次价格（每次运行重新初始化，适合定时任务）
last_prices = {}


def get_stock_price(stock_code):
    """获取股票价格（使用新浪财经API）"""
    try:
        if stock_code.startswith('6'):
            url = f'http://hq.sinajs.cn/list=sh{stock_code}'
        else:
            url = f'http://hq.sinajs.cn/list=sz{stock_code}'

        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'

        if response.status_code == 200:
            data = response.text
            if 'var hq_str_' in data:
                info_str = data.split('"')[1]
                parts = info_str.split(',')

                if len(parts) > 3 and parts[3]:
                    stock_name = parts[0]
              

... (内容过长已截断)
