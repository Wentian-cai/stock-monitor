import requests
import json
from datetime import datetime

# 监控的股票
STOCKS = {
    '600330': {'name': '天通股份', 'category': '上游'},
    '002222': {'name': '福晶科技', 'category': '上游'},
    '300620': {'name': '光库科技', 'category': '中游'},
    '301205': {'name': '联特科技', 'category': '中游'},
    '300502': {'name': '新易盛', 'category': '下游'},
    '000988': {'name': '华工科技', 'category': '下游'}
}

# 价格变化阈值
THRESHOLD = 3.0

# Server酱 SendKey（需要替换为你的SendKey）
SCT_SENDKEY = "oFkBjwdAhVO34o9bP8tfDLqHpD28"

# 是否启用微信通知
ENABLE_WECHAT_NOTIFY = True


def get_stock_price(stock_code):
    """获取股票价格"""
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
        print(f"获取 {stock_code} 价格失败: {str(e)}")
        return None


def check_price_change(stock_code, current_data):
    """检查价格变化"""
    change_pct = current_data['change_pct']

    if abs(change_pct) >= THRESHOLD:
        alert = {
            'stock_code': stock_code,
            'stock_name': current_data['name'],
            'category': STOCKS[stock_code]['category'],
            'current_price': current_data['price'],
            'change_pct': change_pct,
            'direction': '上涨' if change_pct > 0 else '下跌',
            'timestamp': current_data['timestamp']
        }
        
        # 发送微信消息提醒
        if ENABLE_WECHAT_NOTIFY:
            send_wechat_notification(alert)
        
        return alert

    return None


def send_wechat_notification(alert):
    """使用 Server酱发送微信通知"""
    try:
        if SCT_SENDKEY == "YOUR_SENDKEY_HERE":
            print("⚠️  请先配置 SCT_SENDKEY")
            return
        
        url = f"https://sctapi.ftqq.com/{SCT_SENDKEY}.send"
        
        # 构建消息内容
        emoji = "📈" if alert['direction'] == "上涨" else "📉"
        
        message_body = f"""
【{emoji} 股价波动提醒】

📊 股票名称：{alert['stock_name']}
🏷️  所属分类：{alert['category']}
💰 当前价格：¥{alert['current_price']:.2f}
📈 涨跌幅：{alert['direction']} {abs(alert['change_pct']):.2f}%
🕐 时间：{alert['timestamp']}

---
薄膜铌酸锂概念股监控
        """.strip()
        
        data = {
            'title': f"{alert['stock_name']} {alert['direction']} {abs(alert['change_pct']):.2f}%",
            'desp': message_body
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                print(f"✅ 微信通知已发送: {alert['stock_name']}")
            else:
                print(f"❌ 微信通知发送失败: {result.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 发送微信消息失败: {str(e)}")


def main(event):
    """主函数"""
    print("=" * 80)
    print("薄膜铌酸锂概念股监控 - 微信云开发版本（带消息推送）")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"监控股票数: {len(STOCKS)}")
    print(f"价格阈值: {THRESHOLD}%")
    print(f"微信通知: {'启用' if ENABLE_WECHAT_NOTIFY else '禁用'}")
    print("=" * 80)

    results = {}
    alerts = []

    for stock_code, stock_info in STOCKS.items():
        stock_name = stock_info['name']
        category = stock_info['category']

        stock_data = get_stock_price(stock_code)

        if stock_data:
            results[stock_code] = stock_data

            change_str = f"{stock_data['change_pct']:+.2f}%"
            if stock_data['change_pct'] > 0:
                change_str = f"📈 {change_str}"
            elif stock_data['change_pct'] < 0:
                change_str = f"📉 {change_str}"

            print(f"{stock_name}({stock_code}) [{category}]: ¥{stock_data['price']:.2f} {change_str}")

            alert = check_price_change(stock_code, stock_data)
            if alert:
                alerts.append(alert)

        else:
            print(f"❌ {stock_name}({stock_code}): 获取数据失败")

    print("\n" + "=" * 80)
    print("监控汇总")
    print("=" * 80)

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

    return {
        'success': True,
        'success_count': len(results),
        'total_count': len(STOCKS),
        'alerts': alerts,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
