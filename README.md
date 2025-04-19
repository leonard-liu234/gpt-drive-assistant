# GPT Drive Assistant

一个用于生成厨房确认函 PPT 并读取 Google Drive 文件夹的 ChatGPT 插件。

---

## ✨ 功能

- 根据项目数据自动生成 PowerPoint 文件
- 读取指定 Google Drive 文件夹下的文件列表
- 可部署为 ChatGPT 插件并与 Google 账号集成

---

## 🗂️ 项目结构

```
.
├── app.py                   # 主程序：Flask 路由和功能接口
├── openapi.yaml             # 插件接口描述
├── render.yaml              # Render 部署配置
├── requirements.txt         # Python 依赖列表
├── static/                  # 插件 logo、法律信息等资源
│   ├── logo.png
│   └── legal.html
├── well_known/              # 插件入口（自动映射为 /.well-known/ai-plugin.json）
│   └── ai-plugin.json
└── .env.example             # 环境变量模板
```

---

## 🚀 快速部署（Render）

1. Fork 本项目到你自己的 GitHub 账号
2. 登录 [Render.com](https://render.com) 并创建 Web Service
3. 绑定本项目 Git 仓库，并确保：
   - `Start Command`: `gunicorn app:app`
   - `Build Command`: `pip install -r requirements.txt`
4. 添加环境变量（如 `GDRIVE_ACCESS_TOKEN`）
5. 启动成功后可访问：

```
https://your-app.onrender.com/.well-known/ai-plugin.json
```

---

## 📄 插件测试路径

| 路径 | 功能说明 |
|------|----------|
| `/generate-ppt` | 生成 PPT |
| `/folders/<folder_id>/list` | 列出 Google Drive 文件夹 |
| `/.well-known/ai-plugin.json` | 插件入口文件 |

---

## 📬 联系方式

- 负责人: Leonard Liu
- 邮箱: leo1992ljt@gmail.com