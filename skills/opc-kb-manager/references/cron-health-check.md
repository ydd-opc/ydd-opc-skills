# Cron 每日情报流水线 — 健康检查指南

> 用于在 cron job 执行前验证全部依赖项是否就绪。
> 目标：在 9:00 AM 前发现并报告可修复的问题，而不是等推送失败才排查。

## 检查流程（7 层）

### Layer 1: Cron Job 自身状态

```bash
hermes cron list
```

确认项：
- `state` = `scheduled`（不是 paused/errored）
- `enabled` = `true`
- `next_run_at` 显示正确的下一执行时间
- `last_status` = `ok`
- `profile` 指向正确的 profile（通常是 `librarian`）
- `model` + `provider` 与 profile config 一致

### Layer 2: Profile 存在性 + 环境变量

Profile 目录：`D:/soft/hermes/profiles/<name>/`（**不是 `~/.hermes/profiles/`**）

```bash
ls D:/soft/hermes/profiles/<name>/
cat D:/soft/hermes/profiles/<name>/.env     # 应有 DEEPSEEK_API_KEY + SILICONFLOW_API_KEY + 微信凭证
cat D:/soft/hermes/profiles/<name>/config.yaml  # 应有 model.provider + model.model
```

### Layer 3: Gateway 进程 + 连接状态

Gateway 以 `pythonw.exe` 运行（不是 `python.exe`）。

```bash
# 检查进程是否存在
tasklist | grep -i "pythonw"

# 查看进程命令行确认是 gateway
powershell -NoProfile -Command \
  'Get-WmiObject Win32_Process -Filter "ProcessId=<PID>" | Select-Object ProcessId,Name,CommandLine | Format-List'

# 查看 gateway log 确认 WeChat 已连接
tail -5 D:/soft/hermes/logs/gateway.log
```

Gateway 正常运行的日志特征：
```
Gateway running with 1 platform(s)
✓ weixin connected
Cron ticker started (interval=60s)
```

Gateway **未运行**时的处理：
```bash
hermes gateway start        # 前台启动
# 或者通过 Scheduled Task
schtasks /run /tn Hermes_Gateway
```

### Layer 4: Scheduled Tasks 状态

```bash
# Gateway 任务
powershell -NoProfile -Command \
  '$task = Get-ScheduledTask -TaskName "Hermes_Gateway";'`
  'Write-Output ("State: " + $task.State);'`
  'Write-Output ("Enabled: " + $task.Enabled);'`
  'Write-Output ("LastResult: " + ($task | Get-ScheduledTaskInfo).LastTaskResult)'

# WakeUp 任务
powershell -NoProfile -Command \
  '$task = Get-ScheduledTask -TaskName "Hermes_WakeUp";'`
  'Write-Output ("State: " + $task.State);'`
  'Write-Output ("WakeToRun: " + $task.Settings.WakeToRun);'`
  '$trg = $task.Triggers[0];'`
  'Write-Output ("Trigger: " + $trg.GetType().Name);'`
  'Write-Output ("Start: " + $trg.StartBoundary);'`
  'Write-Output ("DaysInterval: " + $trg.DaysInterval);'`
  '$info = $task | Get-ScheduledTaskInfo;'`
  'Write-Output ("LastRun: " + $info.LastRunTime);'`
  'Write-Output ("LastResult: " + $info.LastTaskResult)'
```

确认项：\n- **Hermes_Gateway**: State=Running or Ready\n- **Hermes_Gateway_Starter**: State=Ready（2026-06-07 创建，每日 08:55 自动启动 Gateway 进程。如果此任务缺失，需要重建）\n- **Hermes_WakeUp**: State=Ready, WakeToRun=True, DaysInterval=1（每日触发）
  - StartBoundary 在过去的日期没关系，有 DaysInterval=1 就会每日重复

**git-bash 中 PowerShell 的 $ 变量转义**：在 git-bash 中 PowerShell 变量以 `$` 开头，会被 bash 解释。
解决方案：对整体 PowerShell 命令用单引号包裹（`'...'`），内部的变量访问用双引号字符串拼接或 `Write-Output`。

### Layer 5: 工作目录

```bash
ls -d D:/opc-workdown/Horizon-main/       # Horizon 源码
ls -d D:/opc-workdown/horizon-venv/      # 虚拟环境
ls D:/opc-workdown/siliconflow_gen.py    # 封面图片生成脚本
```

### Layer 6: 历史产出

检查流水线近期是否正常产出：

```bash
ls D:/opc-workdown/AI-Daily-Reports/raw/   # Horizon 日报原始文件
ls D:/opc-workdown/wiki/horizon/           # wiki 消化页面目录
cat D:/opc-workdown/log/20260606.md        # 最近一次运行日志
```

期望：最近至少 1-2 天有产出。如果连续 3+ 天空白则说明流水线可能已中断。

### Layer 7: 时间确认

```bash
date '+%Y-%m-%d %H:%M:%S %:z'
hermes cron list | grep next_run_at
```

确认 `next_run_at` 是否与预期一致（注意时区 +08:00）。

## PythonW 与 Python.exe 的区别

| 进程 | 用途 | 特征 |
|------|------|------|
| `python.exe` | 普通 Python 进程 | 有控制台窗口，占用显存 ~20-180MB |
| `pythonw.exe` | 无窗口 Python 进程 | **Gateway 专用**，~4MB 内存，运行 `-m hermes_cli.main gateway run` |

检查 gateway 时始终查 `pythonw.exe`，不是 `python.exe`。

## 常见问题及处理

### 1. Cron job 的 profile 不存在

```
cronjob list 显示 profile: "librarian"
但 ls D:/soft/hermes/profiles/librarian/ 不存在
```

处理：创建 profile，或修改 cron job 的 profile：

```bash
# 创建 profile
mkdir -p D:/soft/hermes/profiles/librarian/
# 复制 config + .env from an existing profile or root
cp D:/soft/hermes/config.yaml D:/soft/hermes/profiles/librarian/config.yaml
# 编辑 .env 添加需要的 API keys
```

### 2. Gateway 进程没有运行

症状：`tasklist | grep pythonw` 返回空，微信无响应。

处理：
```bash
hermes gateway start
# 等待几秒后检查
tail -5 D:/soft/hermes/logs/gateway.log
```

如果 Gateway 频繁死掉（特别是凌晨时段），原因通常是 Gateway 进程崩溃或系统资源回收。**永久修复**：确保 `Hermes_Gateway_Starter` 任务存在且启用，它每天 08:55 自动重启 Gateway，兼容 WakeUp 唤醒流程。

创建/修复 Starter 任务（无需管理员权限）：
```powershell
$action = New-ScheduledTaskAction -Execute "D:\soft\hermes\hermes-agent\venv\Scripts\pythonw.exe" -Argument "-m hermes_cli.main gateway run"
$trigger = New-ScheduledTaskTrigger -Daily -At 08:55
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "Hermes_Gateway_Starter" -Action $action -Trigger $trigger -Settings $settings -Force
```

### 3. WakeUp 任务上次返回错误码

检查 WakeUp 是否真的触发了唤醒：
- 查看 `D:/soft/hermes/logs/wakeup.log` 内容
- 检查 Scheduled Task 的 LastRunTime 是否接近 8:55 AM
- 如果是华为 MateBook：合盖行为会被华为电脑管家接管，`powercfg` 无效。
  解决方案：保持开盖运行，或者在华为电脑管家中设置合盖不休眠。

### 4. SILICONFLOW_API_KEY 找不到

siliconflow_gen.py 的查找顺序：
1. 环境变量 `SILICONFLOW_API_KEY`
2. 文件 `D:/soft/hermes/.env` 中查找 `SILICONFLOW_API_KEY=`

所以只要 `D:/soft/hermes/.env` 中有 key，即使在 cron job 的 profile 中没设置也能工作。

### 5. 时间理解偏差

如果 cron 的 `next_run_at` 显示的是"今天"但用户说"明天"：
- 凌晨 1-4 点：用户说的"明天"可能实际指"今天早上 9 点"
- 明确告诉用户：`next_run_at = XXXX-XX-XX 09:00 +08:00`，距离现在还有 N 小时

## 快速验证脚本

```bash
# 一行命令检查全部 7 层（需在 git-bash 中执行）
echo "=== Layer 1: Cron ===" && \
hermes cron list && \
echo "=== Layer 4: Tasks ===" && \
powershell -NoProfile -Command '$task=Get-ScheduledTask -TaskName "Hermes_WakeUp"; Write-Output ("WakeUp State="+$task.State+" WakeToRun="+$task.Settings.WakeToRun); $info=$task|Get-ScheduledTaskInfo; Write-Output ("LastRun="+$info.LastRunTime+" Result="+$info.LastTaskResult)' && \
powershell -NoProfile -Command '$task=Get-ScheduledTask -TaskName "Hermes_Gateway"; Write-Output ("Gateway State="+$task.State); $info=$task|Get-ScheduledTaskInfo; Write-Output ("LastRun="+$info.LastRunTime+" Result="+$info.LastTaskResult)' && \
powershell -NoProfile -Command '$task=Get-ScheduledTask -TaskName "Hermes_Gateway_Starter" -ErrorAction SilentlyContinue; if($task){Write-Output ("Starter State="+$task.State)}else{Write-Output "Starter MISSING — auto-start not configured"}' && \
echo "=== Layer 3: Gateway ===" && \
tasklist | grep -i pythonw && \
tail -3 D:/soft/hermes/logs/gateway.log && \
echo "=== Layer 5: Dirs ===" && \
ls -d D:/opc-workdown/Horizon-main D:/opc-workdown/horizon-venv && \
echo "=== Layer 6: History ===" && \
ls D:/opc-workdown/AI-Daily-Reports/raw/ | tail -3 && \
ls D:/opc-workdown/wiki/horizon/ | tail -3
```
