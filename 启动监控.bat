@echo off
chcp 65001 >nul
title 薄膜铌酸锂概念股监控

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║        薄膜铌酸锂概念股实时监控系统                            ║
echo ║                                                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 正在启动股票监控...
echo.
echo 提示：
echo   - 按 Ctrl+C 可以停止监控
echo   - 监控日志会保存到 stock_monitor.log
echo   - 价格提醒会保存到 alerts.json
echo.
echo 正在启动...
echo.

python stock_monitor_configured.py

pause
