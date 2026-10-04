# Calculator Backend

FastAPI 后端，使用递归下降解析器计算表达式，再用 SQLAlchemy 与 psycopg 将成功记录写入 PostgreSQL。所有 API 路径和响应格式保留原样。没有使用 `eval()` 或 `exec()`。

## 结构

```text
app/api/routes.py                 HTTP API
app/calculator/tokenizer.py       词法分析
app/calculator/parser.py          表达式解析与计算
app/database/models.py            SQLAlchemy 表模型
app/database/database.py          PostgreSQL 连接与增删查
app/schemas/schemas.py            请求模型
app/services/calculator_service.py 计算与保存流程
app/main.py                       FastAPI、启动建表
tests/                            解析器、API、数据库 URL 和部署布局测试
```

## 运行与测试

从上级项目根目录按 [总 README](../README.md) 的命令安装、设置 `DATABASE_URL` 并启动。`DATABASE_URL` 必须是 PostgreSQL 连接串，支持 `postgres://` 和 `postgresql://` 自动转换。启动时自动确保 `calculation_history` 表存在。测试命令：

```powershell
.venv\Scripts\python.exe -m pytest calculator_backend/tests -q
```

本地服务：`http://127.0.0.1:8000`；Swagger：`http://127.0.0.1:8000/docs`。历史排序以自增 `id` 倒序，记录时间为 UTC ISO 8601。

| 方法 | 接口 | 说明 |
| --- | --- | --- |
| POST | `/api/calculate` | 成功计算并写入数据库；表达式错误返回 400 |
| GET | `/api/history` | 查询历史 |
| DELETE | `/api/history/{id}` | 删除一条；不存在返回 404 |
| DELETE | `/api/history` | 清空历史 |
