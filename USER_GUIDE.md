# 使用指南

從根目錄 `index.html` 選擇文章。每篇依序完成深入閱讀、情境案例、自我整理、工作紀錄與行動承諾；輸入會保存在目前瀏覽器與網域的 localStorage。

新增文章：在 `content/articles/article_XX/` 放入 `article.md` 與 `article.json`，再執行建置器。文章內容應為原創、去識別化、聚焦一個核心概念或可用工具。

清除瀏覽器網站資料會刪除該網站的學習紀錄；不同網域或預覽網址的保存空間彼此分開。

頁尾提供林祖威教練介紹連結與 LINE 諮詢 QR 圖。
## 修改與發布原則

專案採用「本地優先、明確發布」模式。一般修改只會更新本機檔案，並進行本機建置、結構檢查與必要的 Chrome 互動驗證；不會自動上傳 GitHub，也不會自動部署 Netlify。

只有在使用者明確下達以下指令時，才進行對外同步：

- `push github`：提交並推送至 GitHub
- `更新 Netlify`：建置並部署 Netlify
- `發布`：同步 GitHub 並部署 Netlify

## 作者工作台

啟動本機作者工作台（同時提供公開網站與本機 AI API）：

```bash
python3 scripts/author_server.py
```

開啟 [http://localhost:5200/author-admin.html](http://localhost:5200/author-admin.html)。文章草稿先保存在本機瀏覽器；確認後可匯出備份，再由建置器生成正式文章頁。AI 功能使用本專案 `.env` 的 API 設定，與其他專案分開。
- `只檢查，不發布`：只進行本地與 Chrome 驗證
