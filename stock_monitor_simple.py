"""
简化版股票监控脚本 - 适合GitHub Actions等云端环境
不包含邮件功能，专注于数据获取和记录
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
                    current_price = float(parts[3])
                    prev_close = float(parts[2])

                    if current_price > 0:
                        change_pct = ((current_price - prev_close) / prev_close) * 100

                        return {
                            'code': stock_code,
                            'name': stock_name,
                            'price': current_price,
                            'prev_close': prev_close,
                            'change_pct': change_pct,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }

        return None

    except Exception as e:
        print(f"获取 {stock_code} 价格失败: {str(e)}", file=sys.stderr)
        return None


def log_message(message):
    """记录日志到文件和控制台"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"

    print(log_line)

    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    except Exception as e:
        print(f"写入日志失败: {str(e)}", file=sys.stderr)


def check_price_change(stock_code, current_data):
    """检查价格变化（基于昨日收盘价）"""
    current_price = current_data['price']
    change_pct = current_data['change_pct']

    # 检查相对于昨日收盘价的变化
    if abs(change_pct) >= THRESHOLD:
        return {
            'stock_code': stock_code,
            'stock_name': current_data['name'],
            'category': STOCKS[stock_code]['category'],
            'current_price': current_price,
            'change_pct': change_pct,
            'direction': '上涨' if change_pct > 0 else '下跌',
            'timestamp': current_data['timestamp']
        }

    return None


def save_alert(alert):
    """保存提醒记录"""
    try:
        with open(ALERTS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(alert, ensure_ascii=False) + '\n')
    except Exception as e:
        log_message(f"保存提醒记录失败: {str(e)}")


def main():
    """主函数"""
    print("=" * 80)
    print("薄膜铌酸锂概念股监控 - 云端版本")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"监控股票数: {len(STOCKS)}")
    print(f"价格阈值: {THRESHOLD}%")
    print("=" * 80)

    results = {}
    alerts = []

    for stock_code, stock_info in STOCKS.items():
        stock_name = stock_info['name']
        category = stock_info['category']

        # 获取股价
        stock_data = get_stock_price(stock_code)

        if stock_data:
            results[stock_code] = stock_data

            # 记录数据
            change_str = f"{stock_data['change_pct']:+.2f}%"
            if stock_data['change_pct'] > 0:
                change_str = f"📈 {change_str}"
            elif stock_data['change_pct'] < 0:
                change_str = f"📉 {change_str}"

            log_message(
                f"{stock_name}({stock_code}) [{category}]: "
                f"¥{stock_data['price']:.2f} {change_str}"
            )

            # 检查是否需要提醒
            alert = check_price_change(stock_code, stock_data)
            if alert:
                alerts.append(alert)
                log_message(
                    f"⚠️  提醒: {alert['stock_name']} "
                    f"{alert['direction']} {abs(alert['change_pct']):.2f}%"
                )
                save_alert(alert)

        else:
            log_message(f"❌ {stock_name}({stock_code}): 获取数据失败")

    # 打印汇总
    print("\n" + "=" * 80)
    print("监控汇总")
    print("=" * 80)

    # 按板块分组
    by_category = {}
    for code, data in results.items():
        category = STOCKS[code]['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(data)

    for category, stocks in sorted(by_category.items()):
        print(f"\n【{category}】")
        for stock in stocks:
            change_str = f"{stock['change_pct']:+.2f}%"
            if stock['change_pct'] > 0:
                change_str = f"📈 {change_str}"
            elif stock['change_pct'] < 0:
                change_str = f"📉 {change_str}"

            print(f"  {stock['name']}({stock['code']}): ¥{stock['price']:.2f} {change_str}")

    # 提醒汇总
    if alerts:
        print(f"\n⚠️  本次运行触发 {len(alerts)} 个提醒:")
        for alert in alerts:
            print(f"  - {alert['stock_name']}: {alert['direction']} {abs(alert['change_pct']):.2f}%")
    else:
        print(f"\n✅ 本次运行无价格波动提醒")

    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"成功获取: {len(results)}/{len(STOCKS)}")
    print("=" * 80)

    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main())
