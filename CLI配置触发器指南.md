# 使用 CLI 配置定时触发器

## 📋 准备工作

已经在你的项目中创建了以下文件：
- `cloudbaserc.json` - CloudBase 配置文件
- `config.json` - 云函数配置文件（在云函数中创建）

---

## 🚀 方法1：使用配置文件创建触发器（推荐）

### 步骤1：将 cloudbaserc.json 上传到项目根目录

1. 在微信云开发控制台，找到项目根目录
2. 上传 `cloudbaserc.json` 文件
3. 或者如果使用 CLI 工具，将文件放在项目根目录

### 步骤2：运行命令创建触发器

在命令行中运行：

```bash
# 创建配置文件中定义的所有触发器
tcb fn trigger create
```

或者指定函数名：

```bash
# 为 stock-monitor 函数创建触发器
tcb fn trigger create stock-monitor
```

---

## 🚀 方法2：在云函数中添加 config.json

### 步骤1：在云函数编辑器中创建文件

1. 进入云函数编辑器
2. 创建新文件 `config.json`
3. 粘贴以下内容：

```json
{
  "permissions": {},
  "triggers": [
    {
      "name": "stock-timer",
      "type": "timer",
      "config": "0 */5 * * * * *"
    }
  ]
}
```

### 步骤2：保存并重新部署

1. 保存文件
2. 重新部署云函数
3. 触发器会自动生效

---

## 📝 Cron 表达式说明

`0 */5 * * * * *` 表示：
- 秒：0（第0秒）
- 分：*/5（每5分钟）
- 时：*（每小时）
- 日：*（每天）
- 月：*（每月）
- 周：*（每周）
- 年：*（每年）

**含义**：每5分钟触发一次

### 其他常用表达式

| 表达式 | 含义 |
|--------|------|
| `0 */1 * * * * *` | 每分钟 |
| `0 */10 * * * * *` | 每10分钟 |
| `0 0 * * * * *` | 每小时 |
| `0 0 9 * * * *` | 每天9点 |
| `0 0 9-15 * * MON-FRI *` | 工作日9点-15点每小时 |

---

## 🔧 CLI 命令参考

### 常用命令

```bash
# 查看触发器
tcb fn trigger list

# 创建触发器
tcb fn trigger create [functionName]

# 删除触发器
tcb fn trigger delete <triggerName> [functionName]

# 更新触发器
tcb fn trigger update <triggerName> [functionName]
```

### 帮助信息

```bash
# 查看帮助
tcb fn trigger create --help

# 或
tcb fn --help
```

---

## ✅ 验证触发器是否生效

### 方法1：查看触发器列表

```bash
tcb fn trigger list
```

### 方法2：在控制台查看

1. 进入云函数控制台
2. 找到触发器选项卡
3. 查看是否列出了 `stock-timer`

### 方法3：等待定时触发

等待5分钟，查看云函数日志是否有运行记录

---

## ❓ 常见问题

### Q: 命令提示 "unknown option"
A: 检查命令语法，可能需要使用配置文件方式，而不是命令行参数

### Q: 触发器没有生效
A:
1. 检查 Cron 表达式是否正确
2. 检查函数名称是否匹配
3. 查看云函数日志是否有错误
4. 确认是否在交易时间内（非交易时间无法获取股票数据）

### Q: 如何修改触发器配置
A:
1. 修改 `cloudbaserc.json` 中的配置
2. 删除旧触发器：`tcb fn trigger delete stock-timer stock-monitor`
3. 重新创建：`tcb fn trigger create`

---

## 🎯 推荐操作流程

1. ✅ 在云函数编辑器中创建 `config.json` 文件
2. ✅ 粘贴配置内容
3. ✅ 保存并重新部署函数
4. ✅ 等待5分钟查看是否自动运行

这样不需要使用 CLI，最简单！
