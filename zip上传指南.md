# 微信云开发 ZIP 包上传指南

## 📦 准备部署包

### 方法1：自动创建（推荐）

1. 双击运行 `准备部署包.bat`
2. 会自动创建 `deploy_package` 文件夹，包含：
   - `index.py`（监控代码）
   - `requirements.txt`（依赖文件）

### 方法2：手动创建

1. 创建文件夹 `deploy_package`
2. 复制 `stock_monitor_tcb_simple.py` 到文件夹中
3. 重命名为 `index.py`（微信云开发要求入口文件必须是 index.py）
4. 在文件夹中创建 `requirements.txt` 文件
5. 内容输入：`requests>=2.31.0`

---

## 📤 上传到微信云开发

### 步骤1：压缩文件夹

1. 打开 `deploy_package` 文件夹
2. 右键点击空白处，选择"发送到" → "压缩(zipped)文件夹"
3. 生成 `deploy_package.zip` 文件

### 步骤2：上传到微信云开发

1. 访问微信云开发控制台：https://console.cloud.tencent.com/tcb
2. 进入你的环境
3. 点击"云函数"
4. 点击"新建"或"上传"
5. 选择"上传 zip 包"
6. 上传 `deploy_package.zip`
7. 配置信息：
   - 函数名称：`stock-monitor`
   - 运行环境：`Python 3.9`
   - 入口文件：`index.main`（会自动识别）

### 步骤3：部署完成

1. 等待上传完成
2. 系统会自动安装依赖
3. 点击"测试运行"验证

---

## ⚙️ 配置定时触发器

1. 在云函数页面，点击"触发器"
2. 点击"添加触发器"
3. 配置：
   - 名称：`stock-timer`
   - 类型：定时触发器
   - Cron表达式：`0 */5 * * * * *`（每5分钟执行）
4. 保存

---

## ✅ 验证

1. 点击"测试运行"
2. 查看日志输出
3. 如果有股票波动，检查是否收到微信消息

---

## ❓ 常见问题

### Q: 上传失败怎么办？
A: 检查 zip 文件是否正确，确保包含 `index.py` 和 `requirements.txt`

### Q: 依赖安装失败？
A: 微信云开发会自动安装 requirements.txt 中的依赖，稍等片刻即可

### Q: 找不到 main 函数？
A: 确保 index.py 中有 `def main(event):` 函数

---

## 🎯 完成

部署完成后，云函数会自动每5分钟运行一次，监控股票并发送微信提醒！
