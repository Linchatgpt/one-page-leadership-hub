# Local Development Server

| Project | Port | URL | Start command |
|---|---:|---|---|
| one-page-leadership-hub | 5200 | http://localhost:5200 | `python3 scripts/author_server.py` |

本專案是 Python 建置器產生的純靜態網站，不使用 Vite，因此沒有 `strictPort` 設定。作者工作台與公開網站共用本專案的固定 port；啟動前請確認 `5200` 未被其他程序占用。
