# 薄膜铌酸锂概念股监控脚本 - 快速配置指南

## 📌 第一步：检查配置文件

我已经为您创建了一个配置好的脚本：`stock_monitor_configured.py`

打开这个文件，你会看到顶部的【配置区域】，里面有详细注释。

---

## ⚙️ 第二步：基础配置（必须）

### 1️⃣ 查看默认监控的股票

脚本默认监控以下股票：
```python
STOCKS = {
    '600330': {'name': '天通股份', 'category': '上游'},
    '002222': {'name': '福晶科技', 'category': '上游'},
    '300620': {'name': '光库科技', 'category': '中游'},
    '301205': {'name': '联特科技', 'category': '中游'},
    '300502': {'name': '新易盛', 'category': '下游'},
    '000988': {'name': '华工科技', 'category': '下游'}
}
```

**如何添加/删除股票**：
```python
# 添加新股票
STOCKS = {
    '600330': {'name': '天通股份', 'category': '上游'},
    '300502': {'name': '新易盛', 'category': '下游'},
    '300308': {'name': '中际旭创', 'category': '下游'},  # ← 新增
}

# 删除不想要的股票
# 直接删除对应的行即可
```

### 2️⃣ 设置价格波动阈值

```python
PRICE_CHANGE_THRESHOLD = 3.0  # 涨跌幅超过3%时提醒
```

**推荐设置**：
- **保守型**: 5.0% (只有较大波动才提醒)
- **平衡型**: 3.0% (默认设置，推荐)
- **激进型**: 1.5% (任何小波动都提醒)

### 3️⃣ 设置检查间隔

```python
CHECK_INTERVAL = 300  # 每5分钟检查一次
```

**推荐设置**：
- **5分钟**: 300秒 (推荐，实时性好)
- **10分钟**: 600秒 (平衡)
- **15分钟**: 900秒 (减少API调用)

---

## 📧 第三步：邮件配置（可选）

### 为什么需要邮件提醒？
- ✅ 不用一直盯着屏幕
- ✅ 手机可以收到提醒
- ✅ 有重要波动时及时通知

### 🟢 推荐方案：使用QQ邮箱（免费）

#### 步骤1：获取QQ邮箱授权码

1. 登录你的QQ邮箱：https://mail.qq.com
2. 点击顶部【设置】→【账户】
3. 找到【POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务】
4. 开启【IMAP/SMTP服务】
5. 点击【生成授权码】
6. 按提示发送短信验证
7. 复制生成的授权码（例如：`abcdefghijklmnop`）

**重要**：这是授权码，不是QQ密码！

#### 步骤2：修改脚本配置

在 `stock_monitor_configured.py` 中找到以下部分并修改：

```python
# ==================== 邮件配置（可选）====================

# 启用邮件提醒
EMAIL_ENABLED = True  # ← 改为 True

# QQ邮箱配置
SMTP_CONFIG = {
    'server': 'smtp.qq.com',  # ← 保持不变
    'port': 587,               # ← 保持不变
    'username': 'your_email@qq.com',  # ← 改为你的QQ邮箱
    'password': 'your_auth_code',     # ← 改为刚才获取的授权码
    'from_addr': 'your_email@qq.com',  # ← 改为你的QQ邮箱
    'to_addr': 'your_email@qq.com'     # ← 改为接收提醒的邮箱
}
```

**示例**：
```python
EMAIL_ENABLED = True

SMTP_CONFIG = {
    'server': 'smtp.qq.com',
    'port': 587,
    'username': '123456789@qq.com',
    'password': 'abcdefghijklmnop',
    'from_addr': '123456789@qq.com',
    'to_addr': '123456789@qq.com'
}
```

#### 步骤3：测试邮件

运行脚本，如果配置正确，你会看到：
```
✅ 邮件提醒已发送: 【股价提醒】天通股份(600330) 上涨 3.25%
```

并在邮箱收到提醒邮件。

---

### 🟡 备选方案：使用163邮箱

如果你使用163邮箱，步骤类似：

1. 登录163邮箱：https://mail.163.com
2. 设置 → POP3/SMTP/IMAP
3. 开启SMTP服务并获取授权码
4. 修改配置：

```python
EMAIL_ENABLED = True

SMTP_CONFIG = {
    'server': 'smtp.163.com',  # ← 改为163的SMTP服务器
    'port': 465,                # ← 163使用465端口
    'username': 'your_email@163.com',
    'password': 'your_auth_code',
    'from_addr': 'your_email@163.com',
    'to_addr': 'your_email@163.com'
}
```

---

## ⏰ 第四步：交易时间配置（可选）

### 默认设置

```python
TRADE_TIME_ONLY = True  # 仅在交易时间监控
```

### 交易时间段

```python
TRADE_TIME = {
    'morning_start': '09:30',  # 上午开盘
    'morning_end': '11:30',    # 上午收盘
    'afternoon_start': '13:00', # 下午开盘
    'afternoon_end': '15:00',   # 下午收盘
}
```

**建议**：保持默认设置，只在A股交易时间监控，节省资源。

---

## 🌐 第五步：数据源配置（可选）

```python
DATA_SOURCE = 'sina'  # 可选: 'sina', 'tencent', 'eastmoney'
```

**推荐**：
- `sina` (新浪): 稳定性最好，推荐
- `tencent` (腾讯): 备选方案
- 如果一个不行，可以换另一个试试

---

## 🚀 第六步：运行脚本

### 方法1：直接运行（测试用）

```bash
python stock_monitor_configured.py
```

你会看到类似这样的输出：
```
╔══════════════════════════════════════════════════════════════╗
║                                                                ║
║        薄膜铌酸锂概念股实时监控系统 v2.0                      ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝

配置检查...
  监控股票: 6 只
  价格阈值: 3.0%
  检查间隔: 300 秒
  邮件提醒: 禁用
  交易时间监控: 是

正在启动监控...
```

### 方法2：后台运行（推荐）

#### Windows系统

打开命令提示符，输入：

```bash
start /B python stock_monitor_configured.py > monitor.log 2>&1
```

或者使用 `pythonw`（无窗口运行）：

```bash
pythonw stock_monitor_configured.py
```

#### 使用批处理文件（更方便）

创建一个文件 `启动监控.bat`，内容如下：

```batch
@echo off
chcp 65001 >nul
echo 正在启动股票监控...
python stock_monitor_configured.py
pause
```

双击这个bat文件即可启动监控。

---

## 📊 第七步：查看输出文件

脚本运行后会生成以下文件：

### 1. stock_monitor.log（运行日志）

记录所有监控活动，包括：
- 股价数据获取情况
- 价格波动提醒
- 错误信息

**查看方法**：
```bash
# Windows
type stock_monitor.log

# 或使用记事本打开
notepad stock_monitor.log
```

### 2. alerts.json（历史提醒）

记录所有触发过价格波动的提醒。

**查看方法**：
```bash
# Windows
type alerts.json

# 或使用记事本打开
notepad alerts.json
```

### 3. daily_prices.json（每日价格记录）

每天收盘时的价格记录，方便后续分析。

### 4. startup_log.json（启动记录）

每次脚本启动的记录。

---

## 🎯 快速测试清单

配置完成后，按以下步骤测试：

- [ ] 1. 安装依赖：`pip install -r requirements.txt`
- [ ] 2. 修改配置：打开 `stock_monitor_configured.py` 修改关键配置
- [ ] 3. 测试运行：`python stock_monitor_configured.py`
- [ ] 4. 检查输出：查看是否有股价数据输出
- [ ] 5. 查看日志：打开 `stock_monitor.log` 检查是否有错误
- [ ] 6. （可选）测试邮件：配置邮件并测试接收

---

## ❓ 常见问题

### Q1: 运行提示 "Module not found: requests"

**解决**：
```bash
pip install requests
```

### Q2: 获取不到股价数据

**可能原因**：
- 网络问题 → 检查网络连接
- API限制 → 增加检查间隔时间
- 数据源问题 → 换一个DATA_SOURCE

**解决**：查看日志文件 `stock_monitor.log` 获取详细错误信息。

### Q3: 邮件发送失败

**检查清单**：
1. EMAIL_ENABLED 是否设置为 True
2. 授权码是否正确（不是邮箱密码）
3. SMTP服务器地址和端口是否正确
4. 防火墙是否阻止了邮件发送

### Q4: 脚本运行卡顿

**解决**：
- 增加CHECK_INTERVAL（如改为600秒）
- 减少监控股票数量
- 检查网络连接

---

## 📞 需要帮助？

如果遇到问题：

1. **查看日志**：`stock_monitor.log` 里面有详细的错误信息
2. **检查配置**：确保所有配置项都正确填写
3. **简化测试**：先关闭邮件功能（EMAIL_ENABLED = False），只监控1-2只股票
4. **告诉我**：告诉我具体的错误信息，我帮您解决

---

## 💡 下一步

配置完成后：

1. **测试运行**：先运行一段时间（如1小时）看是否正常
2. **设置开机自启**：配置任务计划程序，开机自动运行
3. **定期检查**：每天查看日志和提醒记录
4. **调整优化**：根据实际运行情况调整参数

---

**提示**：第一次使用建议先不启用邮件，运行一段时间确认脚本正常后再配置邮件功能。
