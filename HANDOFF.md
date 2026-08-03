# Handoff

本專案是由文章設定檔自動產生的 One-Page Leadership Hub。來源資料位於 `content/articles/article_XX/`，不要只直接修改生成 HTML。

## 建置

```bash
python3 scripts/build_article_hub.py
```

輸出為根目錄的 `index.html` 與 `Article_Learning_ArticleXX.html`。互動資料使用瀏覽器 localStorage，不需要登入或雲端同步。

## 目前文章

01 回饋與行動、02 EQ 與團隊、03 當責與行動力。

Article 03 的內容主線為：確認事實、辨認解讀、找到自己的承擔、對齊下一步。

品牌資產：`assets/line-qr.png`。全站頁首 logo 使用 `LE`，品牌名稱使用「精萃領導™學習中心」；頁尾含林祖威教練連結。

主目錄左側的教練介紹為精簡版內容，完整介紹連至 `https://leading4elite.com/about_wesley/`。
- 主目錄在寬度 900px 以下的手機版隱藏左側教練介紹欄位，桌面版維持顯示。
- 主目錄桌面版的上方品牌與左側教練介紹欄對齊；頁尾品牌與教練連結與右側文章地圖欄左緣對齊。
- 所有頁尾均包含精萃領導™學習中心、林祖威教練、`wesley.lin@leading4elite.com` mailto 連結與 LINE QR Code。
- Email 連結使用 Gmail 寫信網址；需先登入 Google 才能直接進入寫信畫面。
- 文章頁桌面版欄位與主目錄一致；上方品牌對齊左側章節欄，頁尾品牌與聯絡資訊對齊右側文章欄。
- Netlify site：`one-page-leadership-hub`；公開網址：https://one-page-leadership-hub.netlify.app；建置指令為 `python3 scripts/build_article_hub.py`，發布目錄為 `.`。
