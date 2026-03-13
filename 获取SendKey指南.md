# 如何获取 Server酱 SendKey

由于原 SendKey 已过期，您需要重新获取一个新的。

## 方法1：使用新的 Server酱 Turbo 版

1. 访问官方页面：
   - https://sct.ftqq.com/ （新版本）
   - 或 https://ftqq.com/ （方糖气球主页）

2. 微信扫码登录

3. 获取新的 SendKey

## 方法2：使用旧版 Server酱

1. 访问：http://sc.ftqq.com/

2. 微信扫码登录

3. 复制您的 SendKey

## 测试 SendKey

获取到新的 SendKey 后，在浏览器中测试：

```
https://sctapi.ftqq.com/你的SendKey.send?title=测试消息
```

如果收到微信消息，说明 SendKey 有效。

## 更新脚本

测试成功后，将新的 SendKey 填入 `stock_monitor.py` 文件第24行：

```python
# Server酱 SendKey
SCT_SENDKEY = "你的新SendKey"
```

然后提交并推送到 GitHub 即可。
