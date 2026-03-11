# 股票监控脚本云端运行方案

## 🌟 推荐方案对比

| 方案 | 成本 | 难度 | 稳定性 | 推荐度 |
|------|------|------|--------|--------|
| **GitHub Actions** | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **PythonAnywhere** | 免费/付费 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Repl.it** | 免费 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **阿里云函数计算** | 免费额度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **腾讯云函数** | 免费额度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **AWS Lambda** | 免费额度 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🏆 方案一：GitHub Actions（最推荐）

### ✅ 优势
- 完全免费
- 配置简单
- 自动定时运行
- 支持邮件通知
- 有完整的日志记录

### ⚙️ 配置步骤

#### 第1步：创建GitHub仓库
1. 访问 https://github.com 注册/登录
2. 创建新仓库：`stock-monitor`
3. 上传脚本文件

#### 第2步：创建工作流配置

在仓库中创建 `.github/workflows/stock-monitor.yml`：

```yaml
name: 股票监控

on:
  # 定时运行（使用UTC时间）
  schedule:
    # 每5分钟运行一次（国内时间+8小时）
    - cron: '*/5 * * * *'

  # 允许手动触发
  workflow_dispatch:

  # 推送代码时也运行（测试用）
  push:
    branches: [ main ]

jobs:
  monitor:
    runs-on: ubuntu-latest

    steps:
    - name: 检出代码
      uses: actions/checkout@v3

    - name: 设置Python环境
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install requests

    - name: 运行监控脚本
      env:
        # 在GitHub Secrets中配置这些环境变量
        EMAIL_ENABLED: ${{ secrets.EMAIL_ENABLED }}
        SMTP_SERVER: ${{ secrets.SMTP_SERVER }}
        SMTP_PORT: ${{ secrets.SMTP_PORT }}
        SMTP_USERNAME: ${{ secrets.SMTP_USERNAME }}
        SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
        EMAIL_TO: ${{ secrets.EMAIL_TO }}
      run: python stock_monitor_configured.py

    - name: 上传日志
      uses: actions/upload-artifact@v3
      with:
        name: monitor-logs
        path: |
          stock_monitor.log
          alerts.json
          daily_prices.json

    - name: 发送邮件通知（使用GitHub Action）
      if: always()
      uses: dawidd6/action-send-mail@v3
      with:
        server_address: ${{ secrets.SMTP_SERVER }}
        server_port: ${{ secrets.SMTP_PORT }}
        username: ${{ secrets.SMTP_USERNAME }}
        password: ${{ secrets.SMTP_PASSWORD }}
        subject: 股票监控运行完成 - ${{ github.job }}
        body: 股票监控任务已完成，请查看日志。
        to: ${{ secrets.EMAIL_TO }}
        from: Stock Monitor
```

#### 第3步：配置GitHub Secrets

在GitHub仓库设置中添加Secrets：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下Secrets：

| Secret名称 | 值示例 | 说明 |
|-----------|--------|------|
| `EMAIL_ENABLED` | `True` | 是否启用邮件 |
| `SMTP_SERVER` | `smtp.qq.com` | SMTP服务器 |
| `SMTP_PORT` | `587` | 端口 |
| `SMTP_USERNAME` | `你的邮箱@qq.com` | 邮箱账号 |
| `SMTP_PASSWORD` | `你的授权码` | 邮箱授权码 |
| `EMAIL_TO` | `你的邮箱@qq.com` | 接收通知的邮箱 |

#### 第4步：推送代码

```bash
git init
git add .
git commit -m "添加股票监控脚本"
git branch -M main
git remote add origin https://github.com/你的用户名/stock-monitor.git
git push -u origin main
```

### 📊 查看结果

在GitHub Actions页面查看：
- 运行状态
- 日志输出
- 下载的日志文件

---

## 🎯 方案二：PythonAnywhere（最简单）

### ✅ 优势
- 专门为Python设计
- 有免费套餐
- 网页界面操作
- 支持定时任务

### ⚙️ 配置步骤

#### 第1步：注册账户

1. 访问 https://www.pythonanywhere.com
2. 注册免费账户

#### 第2步：上传文件

1. 进入 Files 页面
2. 上传 `stock_monitor_configured.py`

#### 第3步：配置邮件（可选）

如果需要邮件通知，修改脚本中的邮件配置。

#### 第4步：设置定时任务

1. 进入 Tasks 页面
2. 点击 "Add a new scheduled task"
3. 填写：
   - Description: `股票监控`
   - Command: `python3 /home/你的用户名/stock_monitor_configured.py >> /home/你的用户名/monitor.log 2>&1`
   - Interval: Every 5 minutes
   - 点击 "Save"

### 💡 免费套餐限制

- 每天运行最多100个任务
- 每个任务最长30秒
- 如果脚本运行时间超过限制，升级到付费套餐

---

## ☁️ 方案三：阿里云函数计算（国内推荐）

### ✅ 优势
- 国内访问速度快
- 有免费额度
- 按需计费，很便宜
- 适合国内使用

### ⚙️ 配置步骤

#### 第1步：开通函数计算

1. 访问 https://fc.console.aliyun.com
2. 开通服务（有免费额度）

#### 第2步：创建函数

1. 选择 "使用内置运行时创建"
2. 运行时：Python 3.9
3. 代码上传方式：在线编辑
4. 函数名称：`stock_monitor`

#### 第3步：编写函数代码

```python
import json
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 监控的股票
STOCKS = {
    '600330': '天通股份',
    '002222': '福晶科技',
    '300620': '光库科技',
    '301205': '联特科技',
    '300502': '新易盛',
    '000988': '华工科技'
}

def handler(event, context):
    """函数入口"""
    logger.info("股票监控开始执行")

    results = {}

    for code, name in STOCKS.items():
        try:
            # 获取股价（使用新浪API）
            if code.startswith('6'):
                url = f'http://hq.sinajs.cn/list=sh{code}'
            else:
                url = f'http://hq.sinajs.cn/list=sz{code}'

            response = requests.get(url, timeout=10)
            response.encoding = 'gbk'

            if response.status_code == 200:
                data = response.text
                if 'var hq_str_' in data:
                    info_str = data.split('"')[1]
                    parts = info_str.split(',')

                    if len(parts) > 3 and parts[3]:
                        price = float(parts[3])
                        prev_close = float(parts[2])
                        change_pct = ((price - prev_close) / prev_close) * 100

                        results[code] = {
                            'name': name,
                            'price': price,
                            'change_pct': change_pct
                        }

                        logger.info(f"{name}({code}): ¥{price:.2f} ({change_pct:+.2f}%)")

        except Exception as e:
            logger.error(f"获取{name}({code})股价失败: {str(e)}")

    # 返回结果
    return {
        'statusCode': 200,
        'body': json.dumps(results, ensure_ascii=False, indent=2)
    }
```

#### 第4步：配置定时触发器

1. 进入函数详情页
2. 点击 "触发器管理"
3. 添加定时触发器：
   - 名称：`stock-monitor-trigger`
   - 触发方式：定时触发
   - Cron表达式：`*/5 * * * *`（每5分钟）
   - 点击确定

#### 第5步：测试运行

1. 点击 "测试函数"
2. 点击 "执行"
3. 查看执行日志

---

## 🌐 方案四：腾讯云函数（国内备选）

与阿里云函数类似，但使用腾讯云平台。

### 配置步骤

1. 访问 https://console.cloud.tencent.com/scf
2. 创建函数
3. 上传代码（同阿里云）
4. 配置定时触发器
5. 测试运行

---

## 💎 方案五：Repl.it（最简单，适合测试）

### ✅ 优势
- 完全免费
- 在线编辑
- 一键运行
- 支持Always On

### ⚙️ 配置步骤

#### 第1步：创建Repl

1. 访问 https://repl.it
2. 创建新Repl
3. 选择Python语言

#### 第2步：上传代码

将 `stock_monitor_configured.py` 的代码复制到编辑器中。

#### 第3步：配置Keep Alive（保持运行）

1. 点击左侧"Secrets"
2. 添加：`KEY` = `REPLIT_KEEP_ALIVE_TIMEOUT_MS`
3. 值：`60000`（60秒）

#### 第4步：启用Always On

1. 进入Repl设置
2. 开启"Always On"
3. （需要付费账户）

#### 第5步：运行

点击"Run"按钮开始运行。

---

## 📊 方案对比总结

### 🥇 最推荐：GitHub Actions

**适合人群**：
- 已有GitHub账户
- 需要免费方案
- 需要完整日志和通知

**优点**：
- ✅ 完全免费
- ✅ 稳定可靠
- ✅ 自动定时
- ✅ 完整日志
- ✅ 邮件通知

**缺点**：
- ⚠️ 需要GitHub账户
- ⚠️ 定时任务有最少5分钟限制

### 🥈 次推荐：PythonAnywhere

**适合人群**：
- Python新手
- 需要图形界面
- 不想折腾代码

**优点**：
- ✅ 简单易用
- ✅ 有免费套餐
- ✅ 专为Python设计

**缺点**：
- ⚠️ 免费版有限制
- ⚠️ 任务运行时长限制

### 🥉 第三选择：阿里云函数计算

**适合人群**：
- 国内用户
- 需要快速响应
- 已使用阿里云

**优点**：
- ✅ 国内速度快
- ✅ 有免费额度
- ✅ 按需计费

**缺点**：
- ⚠️ 需要配置云服务
- ⚠️ 函数有执行时间限制

---

## 🎯 快速开始指南

### 如果你是新手：

```
推荐顺序：
1. PythonAnywhere（最简单）
2. GitHub Actions（免费+稳定）
3. Repl.it（测试用）
```

### 如果你是开发者：

```
推荐顺序：
1. GitHub Actions（最适合）
2. 阿里云函数计算（国内）
3. PythonAnywhere（备选）
```

---

## 💡 我的建议

**根据您的需求**：

1. **想要最简单** → PythonAnywhere
2. **想要完全免费** → GitHub Actions
3. **想要国内快速** → 阿里云函数计算
4. **只是测试** → Repl.it

---

## 🚀 立即开始

选择一个方案后，我可以帮您：
1. 创建详细的配置文件
2. 提供一键部署脚本
3. 解决运行中的问题

**告诉我您想用哪个方案，我帮您配置！**
