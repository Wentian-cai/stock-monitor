"""
薄膜铌酸锂概念股实时监控脚本 - 配置版
功能：定时获取股价数据，价格波动超过阈值时发送提醒
"""

import requests
import json
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import logging
import os

# ==================== 配置区域 - 请根据需要修改 ====================

# ==================== 基础配置 ====================

# 监控的股票列表（可以添加或删除）
STOCKS = {
    '600330': {'name': '天通股份', 'category': '上游'},
    '002222': {'name': '福晶科技', 'category': '上游'},
    '300620': {'name': '光库科技', 'category': '中游'},
    '301205': {'name': '联特科技', 'category': '中游'},
    '300502': {'name': '新易盛', 'category': '下游'},
    '000988': {'name': '华工科技', 'category': '下游'}
}

# 价格波动阈值（百分比）
# 例如: 3.0 表示涨跌幅超过3%时触发提醒
# 建议: 2.0-5.0 之间，太小会有噪音，太大可能错过重要波动
PRICE_CHANGE_THRESHOLD = 3.0

# 检查间隔（秒）
# 例如: 300 表示每5分钟检查一次
# 建议: 300-600秒（5-10分钟）
# 注意: 间隔太短可能导致API访问频率限制
CHECK_INTERVAL = 300

# ==================== 邮件配置（可选）====================

# 是否启用邮件提醒
EMAIL_ENABLED = False  # 设置为 True 启用

# QQ邮箱配置（推荐，需要授权码）
SMTP_CONFIG = {
    'server': 'smtp.qq.com',
    'port': 587,
    'username': 'your_email@qq.com',  # 替换为你的QQ邮箱
    'password': 'your_auth_code',     # 替换为你的QQ邮箱授权码（非邮箱密码）
    'from_addr': 'your_email@qq.com',  # 替换为你的QQ邮箱
    'to_addr': 'your_email@qq.com'     # 替换为接收提醒的邮箱
}

# 163邮箱配置（备选）
# SMTP_CONFIG = {
#     'server': 'smtp.163.com',
#     'port': 465,
#     'username': 'your_email@163.com',
#     'password': 'your_auth_code',
#     'from_addr': 'your_email@163.com',
#     'to_addr': 'your_email@163.com'
# }

# ==================== 交易时间配置 ====================

# 是否只在交易时间运行
TRADE_TIME_ONLY = True  # True: 仅交易时间监控；False: 24小时监控

# 交易时间段（周一至周五）
TRADE_TIME = {
    'morning_start': '09:30',  # 上午开盘
    'morning_end': '11:30',    # 上午收盘
    'afternoon_start': '13:00', # 下午开盘
    'afternoon_end': '15:00',   # 下午收盘
}

# ==================== 日志配置 ====================

# 日志级别
# DEBUG: 最详细（包含所有调试信息）
# INFO: 一般信息（推荐）
# WARNING: 仅警告和错误
LOG_LEVEL = 'INFO'

# 日志文件路径
LOG_FILE = 'stock_monitor.log'

# ==================== 数据存储配置 ====================

# 历史提醒记录文件
ALERTS_FILE = 'alerts.json'

# 每日价格记录文件
DAILY_PRICES_FILE = 'daily_prices.json'

# ==================== API配置 ====================

# 数据源选择: 'sina', 'tencent', 'eastmoney'
# 推荐: 'sina' (新浪财经API，稳定性较好)
DATA_SOURCE = 'sina'

# API请求超时时间（秒）
REQUEST_TIMEOUT = 10

# ==================== 配置结束 ====================


# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 记录上一次的价格
last_prices = {}


class StockMonitor:
    """股票监控类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def is_trade_time(self):
        """判断当前是否在交易时间内"""
        if not TRADE_TIME_ONLY:
            return True

        now = datetime.now()
        weekday = now.weekday()  # 0=周一, 6=周日

        # 周末不交易
        if weekday >= 5:
            return False

        current_time = now.strftime('%H:%M')

        # 检查是否在交易时间段内
        if (TRADE_TIME['morning_start'] <= current_time <= TRADE_TIME['morning_end'] or
            TRADE_TIME['afternoon_start'] <= current_time <= TRADE_TIME['afternoon_end']):
            return True

        return False

    def get_stock_price_sina(self, stock_code):
        """使用新浪财经API获取股价"""
        try:
            # 构造API URL
            if stock_code.startswith('6'):
                url = f'http://hq.sinajs.cn/list=sh{stock_code}'
            else:
                url = f'http://hq.sinajs.cn/list=sz{stock_code}'

            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.encoding = 'gbk'

            if response.status_code == 200:
                data = response.text

                # 解析新浪API返回的数据
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
            logger.error(f"新浪API获取 {stock_code} 价格时出错: {str(e)}")
            return None

    def get_stock_price_tencent(self, stock_code):
        """使用腾讯财经API获取股价"""
        try:
            # 构造API URL
            if stock_code.startswith('6'):
                url = f'http://qt.gtimg.cn/q=sh{stock_code}'
            else:
                url = f'http://qt.gtimg.cn/q=sz{stock_code}'

            response = self.session.get(url, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                data = response.text
                # 解析腾讯API返回的数据
                if '~' in data:
                    info_str = data.split('"')[1]
                    parts = info_str.split('~')

                    if len(parts) > 4:
                        stock_name = parts[1]
                        current_price = float(parts[3])
                        prev_close = float(parts[4])

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
            logger.error(f"腾讯API获取 {stock_code} 价格时出错: {str(e)}")
            return None

    def get_stock_price(self, stock_code):
        """获取股票价格"""
        if DATA_SOURCE == 'sina':
            return self.get_stock_price_sina(stock_code)
        elif DATA_SOURCE == 'tencent':
            return self.get_stock_price_tencent(stock_code)
        else:
            logger.warning(f"未知的数据源: {DATA_SOURCE}")
            return None

    def check_price_change(self, stock_code, current_data):
        """检查价格是否触发提醒"""
        if stock_code not in last_prices:
            last_prices[stock_code] = current_data['price']
            logger.info(f"首次记录 {current_data['name']}({stock_code}) 基准价格: ¥{current_data['price']:.2f}")
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

        # 每小时更新一次基准价格（避免频繁触发）
        return None

    def send_email_alert(self, alert_data):
        """发送邮件提醒"""
        if not EMAIL_ENABLED:
            return

        try:
            subject = f"【股价提醒】{alert_data['stock_name']}({alert_data['stock_code']}) {alert_data['direction']} {abs(alert_data['change_pct']):.2f}%"

            body = f"""
薄膜铌酸锂概念股 - 股价波动提醒

═══════════════════════════════════════

📊 股票信息
   股票名称: {alert_data['stock_name']}
   股票代码: {alert_data['stock_code']}
   所属板块: {alert_data['category']}

💰 价格变动
   之前价格: ¥{alert_data['last_price']:.2f}
   当前价格: ¥{alert_data['current_price']:.2f}
   波动幅度: {abs(alert_data['change_pct']):.2f}%
   波动方向: {alert_data['direction']}

⏰ 提醒时间: {alert_data['timestamp']}

═══════════════════════════════════════

⚠️  重要提示
   这是自动监控脚本发送的提醒，请结合实际情况做出判断。
   所有数据仅供参考，不构成任何投资建议。
   股市有风险，投资需谨慎。

═══════════════════════════════════════
            """

            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = SMTP_CONFIG['from_addr']
            msg['To'] = SMTP_CONFIG['to_addr']

            with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'], timeout=10) as server:
                server.starttls()
                server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
                server.send_message(msg)

            logger.info(f"✅ 邮件提醒已发送: {subject}")

        except Exception as e:
            logger.error(f"❌ 发送邮件失败: {str(e)}")

    def save_alert(self, alert_data):
        """保存提醒记录到文件"""
        try:
            with open(ALERTS_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert_data, ensure_ascii=False) + '\n')
            logger.info(f"✅ 提醒记录已保存到 {ALERTS_FILE}")
        except Exception as e:
            logger.error(f"❌ 保存提醒记录失败: {str(e)}")

    def save_daily_price(self, stock_data):
        """保存每日价格记录"""
        try:
            # 检查今日是否已有记录
            today = datetime.now().strftime('%Y-%m-%d')
            daily_prices = {}

            if os.path.exists(DAILY_PRICES_FILE):
                with open(DAILY_PRICES_FILE, 'r', encoding='utf-8') as f:
                    daily_prices = json.load(f)

            if today not in daily_prices:
                daily_prices[today] = {}

            daily_prices[today][stock_data['code']] = {
                'name': stock_data['name'],
                'price': stock_data['price'],
                'change_pct': stock_data['change_pct'],
                'time': stock_data['timestamp']
            }

            with open(DAILY_PRICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(daily_prices, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"保存每日价格记录失败: {str(e)}")

    def print_summary(self, stocks_data):
        """打印汇总信息"""
        print("\n" + "=" * 80)
        print(f"📊 薄膜铌酸锂概念股监控汇总 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # 按板块分组
        by_category = {}
        for code, data in stocks_data.items():
            if data:
                category = STOCKS[code]['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(data)

        for category, stocks in by_category.items():
            print(f"\n【{category}】")
            for stock in stocks:
                change_str = f"{stock['change_pct']:+.2f}%"
                if stock['change_pct'] > 0:
                    change_str = f"📈 {change_str}"
                elif stock['change_pct'] < 0:
                    change_str = f"📉 {change_str}"
                else:
                    change_str = f"➡️  {change_str}"

                print(f"  {stock['name']}({stock['code']}): ¥{stock['price']:.2f} {change_str}")

        print("=" * 80)

    def monitor_loop(self):
        """主监控循环"""
        logger.info("=" * 80)
        logger.info("🚀 薄膜铌酸锂概念股监控脚本启动")
        logger.info("=" * 80)
        logger.info(f"📋 监控股票数: {len(STOCKS)}")
        logger.info(f"⏰ 检查间隔: {CHECK_INTERVAL}秒 ({CHECK_INTERVAL//60}分钟)")
        logger.info(f"📊 价格阈值: {PRICE_CHANGE_THRESHOLD}%")
        logger.info(f"🌐 数据源: {DATA_SOURCE}")
        logger.info(f"📧 邮件提醒: {'启用' if EMAIL_ENABLED else '禁用'}")
        logger.info(f"🕐 交易时间监控: {'是' if TRADE_TIME_ONLY else '否'}")
        logger.info("=" * 80)

        # 记录首次启动
        startup_log = {
            'startup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'config': {
                'stocks': list(STOCKS.keys()),
                'threshold': PRICE_CHANGE_THRESHOLD,
                'interval': CHECK_INTERVAL,
                'email_enabled': EMAIL_ENABLED
            }
        }

        with open('startup_log.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(startup_log, ensure_ascii=False) + '\n')

        while True:
            try:
                now = datetime.now()

                # 检查是否在交易时间
                if not self.is_trade_time():
                    logger.info(f"⏰ 非交易时间，等待中... ({now.strftime('%H:%M:%S')})")
                    time.sleep(CHECK_INTERVAL)
                    continue

                logger.info(f"\n🔄 开始新一轮检查 - {now.strftime('%Y-%m-%d %H:%M:%S')}")

                stocks_data = {}
                alerts_triggered = []

                for stock_code in STOCKS.keys():
                    # 获取股价
                    stock_data = self.get_stock_price(stock_code)

                    if stock_data:
                        stocks_data[stock_code] = stock_data

                        logger.info(
                            f"  {stock_data['name']}({stock_code}): "
                            f"¥{stock_data['price']:.2f} "
                            f"({stock_data['change_pct']:+.2f}%)"
                        )

                        # 保存每日价格记录
                        self.save_daily_price(stock_data)

                        # 检查是否需要提醒
                        alert = self.check_price_change(stock_code, stock_data)

                        if alert:
                            alerts_triggered.append(alert)
                            logger.warning(
                                f"  ⚠️  价格波动提醒: {alert['stock_name']} "
                                f"{alert['direction']} {abs(alert['change_pct']):.2f}%"
                            )

                            # 保存到文件
                            self.save_alert(alert)

                            # 发送邮件（如果启用）
                            self.send_email_alert(alert)

                    else:
                        logger.warning(f"  ❌ {STOCKS[stock_code]['name']}({stock_code}): 获取数据失败")

                # 打印汇总
                if stocks_data:
                    self.print_summary(stocks_data)

                if alerts_triggered:
                    logger.warning(f"\n⚠️  本轮共触发 {len(alerts_triggered)} 个提醒")
                else:
                    logger.info(f"\n✅ 本轮无价格波动提醒")

                logger.info(f"\n⏳ 等待 {CHECK_INTERVAL} 秒后继续检查...\n")
                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                logger.info("\n\n👋 收到停止信号，监控脚本退出")
                logger.info("感谢使用！")
                break

            except Exception as e:
                logger.error(f"❌ 监控过程中发生错误: {str(e)}")
                logger.info(f"⏳ 等待 {CHECK_INTERVAL} 秒后重试...\n")
                time.sleep(CHECK_INTERVAL)


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                                ║
║        薄膜铌酸锂概念股实时监控系统 v2.0                      ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    print("配置检查...")
    print(f"  监控股票: {len(STOCKS)} 只")
    print(f"  价格阈值: {PRICE_CHANGE_THRESHOLD}%")
    print(f"  检查间隔: {CHECK_INTERVAL} 秒")
    print(f"  邮件提醒: {'启用' if EMAIL_ENABLED else '禁用'}")
    print(f"  交易时间监控: {'是' if TRADE_TIME_ONLY else '否'}")

    if EMAIL_ENABLED:
        print(f"\n  邮件服务器: {SMTP_CONFIG['server']}")
        print(f"  发送到: {SMTP_CONFIG['to_addr']}")
    else:
        print("\n  💡 提示: 如需邮件提醒，请将 EMAIL_ENABLED 设置为 True")

    print("\n正在启动监控...\n")

    monitor = StockMonitor()

    try:
        monitor.monitor_loop()
    except KeyboardInterrupt:
        print("\n监控已停止")


if __name__ == '__main__':
    main()
