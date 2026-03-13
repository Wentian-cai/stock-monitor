"""
股票监控脚本 - 无需外部依赖
使用 Python 内置的 urllib 库
"""
import urllib.request
import urllib.error
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

# 价格变化阈值（设置为0.1%用于测试）
THRESHOLD = 0.1

# Server酱 SendKey
SCT_SENDKEY = "SCT322095Tc3K3I49Joj8VK32Cu1uAHZfw"

# 是否启用微信通知
ENABLE_WECHAT_NOTIFY = True


def fetch_url(url):
    """使用 urllib 获取网页内容"""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('gbk')
        return content
    except urllib.error.URLError as e:
        print(f"获取 URL 失败: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None


def send_post_request(url, data):
    """发送 POST 请求"""
    try:
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=encoded_data, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
        return content
    except Exception as e:
        print(f"发送 POST 请求失败: {e}")
        return None


def get_stock_price(stock_code):
    """获取股票价格"""
    try:
        if stock_code.startswith('6'):
            url = f'http://hq.sinajs.cn/list=sh{stock_code}'
        else:
            url = f'http://hq.sinajs.cn/list=sz{stock_code}'

        content = fetch_url(url)
        if not content:
            return None

        if 'var hq_str_' in content:
            info_str = content.split('"')[1]
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

    # 测试模式：每次都发送通知（无论是否达到阈值）
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


def send_wechat_notification(alert):
    """使用 Server酱发送微信通知"""
    try:
        if SCT_SENDKEY == "YOUR_SENDKEY_HERE":
            print("⚠️  请先配置 SCT_SENDKEY")
            return

        # 尝试多个 API 地址
        api_urls = [
            f"https://sctapi.ftqq.com/{SCT_SENDKEY}.send",
            f"https://sc.ftqq.com/{SCT_SENDKEY}.send"
        ]

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

        # 尝试每个 API 地址
        for url in api_urls:
            print(f"尝试发送到: {url}")
            content = send_post_request(url, data)

            if content:
                print(f"✅ 微信通知已发送: {alert['stock_name']}")
                return
            else:
                print(f"❌ {url} 发送失败，尝试下一个地址")

        print(f"❌ 所有 API 地址均发送失败")

    except Exception as e:
        print(f"❌ 发送微信消息失败: {str(e)}")


def main():
    """主函数"""
    print("=" * 80)
    print("薄膜铌酸锂概念股监控")
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

    # 保存日志到文件
    with open('stock_monitor.log', 'w', encoding='utf-8') as f:
        f.write(f"薄膜铌酸锂概念股监控\n")
        f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"监控股票数: {len(STOCKS)}\n")
        f.write(f"价格阈值: {THRESHOLD}%\n")
        f.write(f"成功获取: {len(results)}/{len(STOCKS)}\n")
        f.write(f"触发提醒: {len(alerts)}\n")
        f.write("\n详细结果:\n")
        for code, data in results.items():
            f.write(f"{data['name']}({code}): ¥{data['price']:.2f} ({data['change_pct']:+.2f}%)\n")

    # 保存提醒到 JSON 文件
    with open('alerts.json', 'w', encoding='utf-8') as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

    return {
        'success': True,
        'success_count': len(results),
        'total_count': len(STOCKS),
        'alerts': alerts,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == '__main__':
    main()
