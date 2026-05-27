# 阿里国际站询盘日报自动生成器

这个项目会读取指定文件夹里最新的 `询盘_*.xlsx`，自动生成中文询盘日报，并在 SMTP 环境变量配置完整时发送邮件。

## 功能

- 自动读取 `data/inquiries/` 中最新的 `询盘_*.xlsx`
- 优先统计昨天的数据；如果文件里没有昨天，则使用文件中最新日期
- 统计新增询盘数量、国家/地区分布、热门产品 Top 3
- 筛选主题中包含 `sample` 或 `urgent` 的高优先级询盘
- 生成适合手机阅读的 HTML 日报
- 支持 GitHub Actions 每天北京时间 09:00 自动运行

## 本地运行

先安装依赖：

```powershell
python -m pip install -r requirements.txt
```

生成模拟数据：

```powershell
python scripts/generate_sample_data.py
```

生成日报：

```powershell
python scripts/run_report.py
```

生成结果会保存在 `reports/日报_YYYY-MM-DD.html`，图表会保存在 `reports/assets/`。

## 桌面窗口

如果你想用按钮操作，可以运行：

```powershell
python scripts/app_window.py
```

窗口支持：

- 生成示例数据
- 生成日报
- 打开最新日报
- 打开询盘文件夹
- 打开日报文件夹
- 选择询盘文件并提示放置位置

## Excel 字段要求

脚本会自动识别以下字段别名：

- 日期：`日期`、`询盘时间`、`创建时间`、`Created Time`、`Inquiry Date`
- 国家/地区：`国家`、`国家/地区`、`Country`、`Region`
- 产品：`产品`、`产品名称`、`Product`、`Product Name`
- 主题：`主题`、`询盘主题`、`Subject`、`Title`

真实导出的文件只要包含这些字段中的任意一种命名即可。

## 邮件配置

如果要发送邮件，请设置以下环境变量：

```powershell
$env:SMTP_HOST="smtp.example.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="your-account@example.com"
$env:SMTP_PASSWORD="your-password"
$env:MAIL_FROM="your-account@example.com"
$env:MAIL_TO="receiver@example.com"
$env:SMTP_USE_TLS="true"
python scripts/run_report.py
```

如果没有设置完整 SMTP 配置，脚本会跳过邮件发送，只保存本地日报。

## GitHub Actions 配置

`.github/workflows/daily-report.yml` 已配置为北京时间每天 09:00 自动运行。

如需邮件发送，请在 GitHub 仓库的 `Settings -> Secrets and variables -> Actions` 中添加：

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `MAIL_FROM`
- `MAIL_TO`
- `SMTP_USE_TLS`

运行后，日报会作为 workflow artifact 上传。

## 提交到 GitHub

当前本机环境没有可用的 `git` 命令。安装 Git 并配置好远程仓库后，可以执行：

```powershell
git init
git add .
git commit -m "Add Alibaba inquiry daily report generator"
git branch -M main
git remote add origin <你的 GitHub 仓库地址>
git push -u origin main
```
