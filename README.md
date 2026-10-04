# 前后端分离计算器系统 · Vercel 版

原生 HTML/CSS/JavaScript 前端调用同域 `/api/*`；FastAPI 用递归下降解析器完成计算；成功记录保存到 PostgreSQL。页面刷新和 Vercel 重新部署不会清空数据库历史。`calculator_frontend/` 保留独立前端源码，`public/` 是完全相同的 Vercel 静态文件；`calculator_backend/` 是独立后端代码。部署时**把本目录整体放进一个 GitHub 仓库**，不要分别导入两个子目录。课程要求的源码另外放在独立的 [前端仓库](https://github.com/lyweee859-arch/calculator-frontend) 和 [后端仓库](https://github.com/lyweee859-arch/calculator-backend)。

## 目录

```text
app.py                    Vercel FastAPI 入口
dev.py                    本地同域开发入口
vercel.json               框架及根路径路由
public/                   Vercel 静态页面（/、/css/*、/js/*）
calculator_frontend/      前端源码
calculator_backend/app/   API、解析器、PostgreSQL 数据层
calculator_backend/tests/ 自动化测试
requirements.txt          部署依赖
requirements-dev.txt      本地测试依赖
.env.example              环境变量示例
```

## 本地运行

需要 Python 3.12 和一个可访问的 PostgreSQL 数据库。在本目录运行：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:DATABASE_URL = "postgresql://用户名:密码@主机/数据库?sslmode=require"
.venv\Scripts\python.exe -m uvicorn dev:app --reload
```

打开 `http://127.0.0.1:8000`。本地入口把 `public/` 静态页面和 `/api/*` 放在同一个端口，行为与线上同域访问一致。后端启动时自动建表，不需要手工执行 SQL。运行测试：

```powershell
.venv\Scripts\python.exe -m pytest calculator_backend/tests -q
```

测试用临时数据库验证 API，不会清空真实 PostgreSQL 的记录。

## Neon PostgreSQL

1. 在 [Neon 控制台](https://console.neon.tech/) 创建项目和数据库。
2. 在项目 Dashboard 点击 **Connect**，选择数据库和角色，勾选 **Pooled connection**，复制完整的 Connection string（通常含 `sslmode=require`）。
3. 将此字符串作为 `DATABASE_URL` 使用。代码自动接受 `postgres://`、`postgresql://` 或 `postgresql+psycopg://` 前缀，不需要手改。

项目只需要 `DATABASE_URL` 一个自定义环境变量。不要把真实连接串写入仓库或 `.env.example`。

## GitHub 与 Vercel 部署

1. 把**本 README 所在的整个目录**上传到**一个** GitHub 仓库。仓库根目录应直接看见 `app.py`、`vercel.json`、`requirements.txt`、`public/`、`calculator_backend/`。`.gitignore` 会排除 `.env`、本地数据库、虚拟环境和 `.vercel/`。
2. 在 [Vercel](https://vercel.com/) 选择 **Add New → Project → Import Git Repository**，选这个仓库。
3. 设置：**Framework Preset = FastAPI**；**Root Directory = 仓库根目录 `./`**；**Build Command = 保持默认**；**Output Directory = 保持默认**；**Install Command = 保持默认**。仓库里的 `vercel.json` 已指定框架和首页路由。
4. 在导入页的 **Environment Variables** 区域新增 `DATABASE_URL`，值粘贴 Neon 的完整连接串，至少选择 **Production**。项目创建后也可在 **Settings → Environment Variables** 添加或修改。若还要使用预览部署，也给 **Preview** 配置连接串；建议预览使用独立 Neon 分支。
5. 点击 **Deploy**。若首次部署前未添加变量，补上后需 **Redeploy**；环境变量变更不会自动改变已有部署。

Vercel 的 `public/index.html` 对应 `/`，`public/css/*`、`public/js/*` 分别对应 `/css/*`、`/js/*`。仅 `/` 被重写到首页；`/api/*` 由 FastAPI 处理，不会返回 HTML。FastAPI 启动时自动创建 `calculation_history` 表。数据库在 Neon，不保存在 Vercel 文件系统。

## 部署后检查

访问 `https://你的项目.vercel.app/`，再检查：

- `https://你的项目.vercel.app/api/history` 返回 JSON。
- `https://你的项目.vercel.app/docs` 显示 Swagger。
- 页面依次计算 `1+2`、`1+2*3`、`(1+2)*3`、`3*-2`、`3.14*2`，结果应为 `3`、`7`、`9`、`-6`、`6.28`。
- 输入 `1/0` 或 `1++*` 显示错误，历史不增加。
- 删除一条历史、清空历史、刷新页面，并在重新部署或重启后再次打开页面，检查历史与 Neon 数据一致。

本仓库不包含本地数据库文件。旧 SQLite 记录不会自动导入 Neon 数据库。

## API

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| POST | `/api/calculate` | 请求 `{"expression":"(1+2)*3"}`；成功后保存历史 |
| GET | `/api/history` | 按新到旧查询历史 |
| DELETE | `/api/history/{id}` | 删除单条，不存在返回 404 |
| DELETE | `/api/history` | 清空历史 |
