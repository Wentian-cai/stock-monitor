# 薄膜铌酸锂概念股监控系统

自动监控股票价格波动，超过阈值时发送微信提醒。

## 功能特点

- ✅ 无需外部依赖（使用 Python 内置库）
- ✅ 每5分钟自动监控
- ✅ 支持6只薄膜铌酸锂概念股
- ✅ 价格波动超过3%时发送微信通知
- ✅ 完全免费（GitHub Actions）

## 监控股票

### 上游
- 天通股份 (600330)
- 福晶科技 (002222)

### 中游
- 光库科技 (300620)
- 联特科技 (301205)

### 下游
- 新易盛 (300502)
- 华工科技 (000988)

## 部署步骤

### 1. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建新仓库 `stock-monitor`
3. 上传以下文件：
   - `stock_monitor.py` - 监控脚本
   - `.github/workflows/stock-monitor.yml` - GitHub Actions 配置

### 2. 配置 GitHub Actions

上传文件后，GitHub Actions 会自动运行。

### 3. 查看运行结果

在 GitHub 仓库的 "Actions" 标签页查看运行日志。

## 配置微信推送

### 获取 Server酱 SendKey

1. 访问 https://sctapi.ftqq.com/
2. 微信扫码登录
3. 获取 SendKey

### 修改脚本

编辑 `stock_monitor.py`，修改第20行的 SendKey：

```python
SCT_SENDKEY = "你的SendKey"
```

## 自定义配置

### 修改监控股票

编辑 `stock_monitor.py` 中的 `STOCKS` 字典：

```python
STOCKS = {
    '600330': {'name': '天通股份', 'category': '上游'},
    # 添加更多股票...
}
```

### 修改价格阈值

修改第16行：

```python
THRESHOLD = 3.0  # 3% 波动触发提醒
```

### 修改监控频率

编辑 `.github/workflows/stock-monitor.yml` 中的 Cron 表达式：

```yaml
schedule:
  - cron: '*/5 * * * *'  # 每5分钟
```

## 工作原理

1. GitHub Actions 每5分钟自动运行
2. 获取股票实时价格
3. 检查价格波动是否超过阈值
4. 超过阈值时通过 Server酱发送微信通知

## 费用说明

完全免费：
- GitHub Actions 每月 2000 分钟免费额度
- Server酱 每天 100 条消息推送免费额度

## 许可证

MIT License
