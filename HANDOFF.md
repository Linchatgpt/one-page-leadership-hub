# Handoff

本專案是由文章設定檔自動產生的 One-Page Leadership Hub。來源資料位於 `content/articles/article_XX/`，不要只直接修改生成 HTML。

目前 ARTICLE 01–07 均已依新版 One Page Hub 規格配置主題插圖；ARTICLE 04–07 的工具卡已用 Markdown inline markers 放置於相關閱讀段落後。

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
- 發布策略採本地優先：除非使用者明確要求 `push github`、`更新 Netlify` 或 `發布`，否則只做本地建置與 Chrome 驗證，不進行外部同步。
- 目前主目錄已重新編碼並顯示 ARTICLE 01–04。
- 目前主目錄顯示 ARTICLE 01–05，ARTICLE 05 為領導力發展與教練學習系統主題。
- 目前主目錄顯示 ARTICLE 01–06，ARTICLE 06 聚焦主管提問、任務交代與可回饋能力。
- 目前主目錄顯示 ARTICLE 01–07，ARTICLE 07 聚焦 1:1 對話與工作現場。
- 工作工具卡由建置器統一補上使用與回看說明；修改工具卡時應保留原本的步驟與文章專屬內容。
- 01 深入閱讀的 `.reading-essay` 與 `.reading-tool` 使用主欄寬度；修改 CSS 後需更新 `article-learning.css?v=YYYYMMDD` 版本參數，避免本地或瀏覽器保留舊樣式。
- 所有文章頁的 03 自我整理區塊預設收起；工具卡包含步驟與延伸說明；章節標題統一採精簡版本。
- 文章頁主內容欄明確限制最大寬度 920px，正文與工具卡最大寬度 780px；03 自我整理收起指示使用 `-`。
- 03 自我整理的互動標示比照 BEFORE YOU READ：預設收合，右側顯示「點擊展開／收起」，展開時以 `-` 表示可收回。
- 文章頁主欄與 section 皆有共用最大寬度限制，04／05 不應因文章內容而展開成全螢幕寬。
- 03 自我整理的 details 容器結構已修正；04 工作紀錄與 05 行動承諾保持在文章主欄內。
- 04 工作紀錄與 05 行動承諾使用 `max-width: 920px`，與 03 自我整理外框及文章主欄對齊。
- 目前主目錄顯示 ARTICLE 01–04；舊版被移除的原 article_01 已保留於 `content/archive/article_legacy_01/`，不會由建置器讀取。
