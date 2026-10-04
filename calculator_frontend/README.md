# Calculator Frontend

原生 HTML、CSS、JavaScript 和 Fetch API。页面只处理输入、显示和历史交互；计算与历史持久化由同域 `/api/*` 的 FastAPI 后端完成。`localStorage` 只保存主题设置。

```text
index.html      页面结构
css/style.css   响应式布局与主题
js/app.js       API 请求、按键和历史操作
```

Vercel 从项目根目录的 `public/` 提供这些文件；`public/` 与本目录的页面文件完全相同。部署时应上传**整个上级项目目录**，不要仅上传本目录。后端地址固定使用相对路径 `/api`，无需配置公网域名或 CORS。

本地运行及部署步骤见 [总 README](../README.md)。支持键盘输入、Enter 计算、Backspace 退格、Escape 清空、历史查询/搜索/删除/清空、错误提示和深色模式。
