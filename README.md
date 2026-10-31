# LearnHub · 学习坊

免费的中英文编程学习平台，Vue 3 + TypeScript + Flask + SQLite。支持课程浏览、手机号注册登录、课时学习、进度保存、视频续播、结课测验与成绩记录、管理后台和 DeepSeek 学习助手。界面采用黑白配色，右上角“登录”内可以切换注册。主题默认为跟随系统，也可切换浅色或深色模式；选择保存在当前浏览器中。

## Windows 启动

实测工具版本：Python **3.14.2**、Node **24.12.0**、npm **11.6.2**。这台工作区的工具在忽略提交的 `.tools` 中；新电脑需自行安装工具，并重新安装项目依赖。

首次在项目根目录双击 `setup.bat`，或执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

日常启动双击 `start.bat`，或执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

浏览器访问 http://127.0.0.1:5000 。保持终端打开，Ctrl+C 停止。启动脚本执行迁移和幂等课程初始化，再构建前端、启动 Waitress。现有账号、进度、成绩和人工编辑不会被清空。

也可用 PyCharm 打开整个项目，解释器选择 `backend/.venv/Scripts/python.exe`。先运行一次 start.bat 生成前端构建，再停止服务；之后右键 `backend/run.py` → Run，即可通过同一地址启动。修改前端代码后需重新构建或使用开发模式。

## 管理员与账号

“我的学习 → 成绩记录”可查看历次分数和解析；课程下架后，已有成绩仍可查看。

学员在网页自行注册，无短信、无公开默认管理员密码。创建管理员：

```powershell
cd backend
.\.venv\Scripts\python.exe -m flask --app app:create_app create-admin
```

按提示输入手机号和密码，再使用该账号登录网页，进入“管理后台”。管理员可维护双语分类、课程、章节、课时、测验，发布/下架课程，搜索和启停普通账号。修改已发布课程前需先下架；归档保留学习历史。发布需完整双语内容、有效课时及至少 3 道有效题目。

忘记密码通过本地命令重置，旧会话会失效：

```powershell
.\.venv\Scripts\python.exe -m flask --app app:create_app reset-password
```

## DeepSeek

在 `backend/.env` 填写 `DEEPSEEK_API_KEY` 后重启。Key 仅由后端读取。默认模型由 `DEEPSEEK_MODEL` 配置。未配置时页面明确提示，其他学习功能仍可使用。对话只保留在当前页面，不持久化。

## 开发与测试

开发时在两个终端分别运行：

```powershell
# 终端 A：backend 目录
.\.venv\Scripts\python.exe -m flask --app app:create_app run --host 127.0.0.1 --port 5000 --debug
# 终端 B：frontend 目录（使用 Node 24）
npm.cmd run dev
```

访问 http://127.0.0.1:5173 。如用项目自带 Node，先在项目根目录设置 `$env:Path = "$PWD\.tools\node-v24.12.0-win-x64;$env:Path"`。

```powershell
# backend
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
# frontend
npm.cmd test
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
```

E2E 在临时数据库和 5001/5174 端口运行，管理员/学员测试账号仅存在于临时库，不修改日常数据。演示视频为原创 12 秒无声素材，源码在 `scripts/generate_demo_video.py`；日常运行无需安装 FFmpeg。

## 数据与换电脑

SQLite 固定在 `backend/instance/learnhub.db`，不依赖启动目录。备份可在根目录执行：

```powershell
.\backend\.venv\Scripts\python.exe scripts/backup_db.py
```

备份输出至 `backend/instance/backups/`。恢复前停止服务，备份当前文件，再用所选备份替换 `learnhub.db`。不要通过 Git 合并数据库。

新电脑获取同一提交/标签，安装相同工具，执行 setup.bat，创建自己的管理员。`.env`、密钥、instance、虚拟环境、node_modules、构建产物均不提交；两台电脑账号和学习记录各自独立。`SECRET_KEY` 留空时会在 instance 中生成随机密钥，更换密钥将退出旧会话。支持通过 `LEARNHUB_PYTHON` 环境变量指定本机 Python 路径。

macOS/Linux：在 backend 执行 `python3.14 -m venv .venv`、`.venv/bin/python -m pip install -r requirements.txt`、复制 `.env.example` 为 `.env`、`db upgrade`、`seed-demo`；frontend 执行 `npm ci && npm run build`；然后从 backend 执行 `.venv/bin/python run.py`。此流程尚待对应操作系统实测。

本机详细检查与交接记录保存在 `docs/`，按用户要求不加入 Git。本项目尚未发布到公网，朋友电脑需在目标机实际验收。
