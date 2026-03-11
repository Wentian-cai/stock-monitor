"""
薄膜铌酸锂概念股实时监控脚本
功能：定时获取股价数据，价格波动超过阈值时发送提醒
"""

import requests
import json
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 监控的股票列表
STOCKS = {
    '600330': {'name': '天通股份', 'category': '上游'},
    '002222': {'name': '福晶科技', 'category': '上游'},
    '300620': {'name': '光库科技', 'category': '中游'},
    '301205': {'name': '联特科技', 'category': '中游'},
    '300502': {'name': '新易盛', 'category': '下游'},
    '000988': {'name': '华工科技', 'category': '下游'}
}

# 价格波动阈值（百分比）
PRICE_CHANGE_THRESHOLD = 3.0  # 涨跌幅超过3%触发提醒

# 检查间隔（秒）
CHECK_INTERVAL = 300  # 5分钟检查一次

# 记录上一次的价格
last_prices = {}

# 邮件通知配置（可选）
EMAIL_CONFIG = {
    'enabled': False,  # 设置为True启用邮件通知
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'username': 'your_email@example.com',
    'password': 'your_password',
    'from_addr': 'your_email@example.com',
    'to_addr': 'your_email@example.com'
}


class StockMonitor:
    """股票监控类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_price(self, stock_code):
        """
        获取股票价格（使用免费API）
        注意：实际使用时需要替换为可用的免费API
        """
        try:
            # 这里使用示例URL，实际需要替换为真实的免费API
            # 常见免费API选择：
            # 1. 新浪财经API: http://hq.sinajs.cn/list=股票代码
            # 2. 腾讯财经API: http://qt.gtimg.cn/q=股票代码
            # 3. 东方财富API
            # 4. Yahoo Finance API（可能需要科学上网）

            # 示例：使用新浪财经API（上海交易所股票）
            if stock_code.startswith('6'):
                url = f'http://hq.sinajs.cn/list=sh{stock_code}'
            else:
                url = f'http://hq.sinajs.cn/list=sz{stock_code}'

            response = self.session.get(url, timeout=10)
            response.encoding = 'gbk'

            if response.status_code == 200:
                # 解析新浪API返回的数据
                data = response.text
                if 'var hq_str_' in data:
                    # 提取股票信息
                    info_str = data.split('"')[1]
                    parts = info_str.split(',')

                    if len(parts) > 3:
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

            logger.warning(f"未能获取 {stock_code} 的有效数据")
            return None

        except Exception as e:
            logger.error(f"获取 {stock_code} 价格时出错: {str(e)}")
            return None

    def check_price_change(self, stock_code, current_data):
        """检查价格是否触发提醒"""
        if stock_code not in last_prices:
            last_prices[stock_code] = current_data['price']
            return None

        last_price = last_prices[stock_code]
        current_price = current_data['price']

        if last_price > 0:
            change_pct = ((current_price - last_price) / last_price) * 100

            if abs(change_pct) >= PRICE_CHANGE_THRESHOLD:
                # 更新最后价格
                last_prices[stock_code] = current_price

                return {
                    'stock_code': stock_code,
                    'stock_name': current_data['name'],
                    'category': STOCKS[stock_code]['category'],
                    'last_price': last_price,
                    'current_price': current_price,
                    'change_pct': change_pct,
                    'direction': '上涨' if change_pct > 0 else '下跌',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

        # 如果间隔较长，更新基准价格
        last_prices[stock_code] = current_price
        return None

    def send_email_alert(self, alert_data):
        """发送邮件提醒"""
        if not EMAIL_CONFIG['enabled']:
            return

        try:
            subject = f"【股价提醒】{alert_data['stock_name']}({alert_data['stock_code']}) {alert_data['direction']} {abs(alert_data['change_pct']):.2f}%"

            body = f"""
股价波动提醒：

股票名称: {alert_data['stock_name']}
股票代码: {alert_data['stock_code']}
所属板块: {alert_data['category']}
之前价格: ¥{alert_data['last_price']:.2f}
当前价格: ¥{alert_data['current_price']:.2f}
波动幅度: {abs(alert_data['change_pct']):.2f}%
波动方向: {alert_data['direction']}
提醒时间: {alert_data['timestamp']}

这是自动监控脚本发送的提醒，请结合实际情况做出判断。
            """

            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = EMAIL_CONFIG['from_addr']
            msg['To'] = EMAIL_CONFIG['to_addr']

            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls()
                server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                server.send_message(msg)

            logger.info(f"邮件提醒已发送: {subject}")

        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")

    def monitor_loop(self):
        """主监控循环"""
        logger.info("=" * 60)
        logger.info("薄膜铌酸锂概念股监控脚本启动")
        logger.info(f"监控间隔: {CHECK_INTERVAL}秒")
        logger.info(f"价格阈值: {PRICE_CHANGE_THRESHOLD}%")
        logger.info("=" * 60)

        while True:
            try:
                logger.info(f"\n开始新一轮检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                for stock_code in STOCKS.keys():
                    # 获取股价
                    stock_data = self.get_stock_price(stock_code)

                    if stock_data:
                        logger.info(
                            f"{stock_data['name']}({stock_code}): "
                            f"¥{stock_data['price']:.2f} "
                            f"({stock_data['change_pct']:+.2f}%)"
                        )

                        # 检查是否需要提醒
                        alert = self.check_price_change(stock_code, stock_data)

                        if alert:
                            logger.warning(
                                f"⚠️  价格波动提醒: {alert['stock_name']} "
                                f"{alert['direction']} {abs(alert['change_pct']):.2f}%"
                            )

                            # 保存到文件
                            self.save_alert(alert)

                            # 发送邮件（如果启用）
                            self.send_email_alert(alert)

                    else:
                        logger.warning(f"{STOCKS[stock_code]['name']}({stock_code}): 获取数据失败")

                logger.info(f"本轮检查完成，等待{CHECK_INTERVAL}秒后继续...")
                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                logger.info("\n收到停止信号，监控脚本退出")
                break

            except Exception as e:
                logger.error(f"监控过程中发生错误: {str(e)}")
                logger.info(f"等待{CHECK_INTERVAL}秒后重试...")
                time.sleep(CHECK_INTERVAL)

    def save_alert(self, alert_data):
        """保存提醒记录到文件"""
        try:
            with open('alerts.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert_data, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"保存提醒记录失败: {str(e)}")


def main():
    """主函数"""
    monitor = StockMonitor()

    # 启动监控
    try:
        monitor.monitor_loop()
    except KeyboardInterrupt:
        logger.info("监控已停止")


if __name__ == '__main__':
    main()
