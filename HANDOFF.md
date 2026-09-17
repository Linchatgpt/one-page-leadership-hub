# Handoff

## 2026-09-11：目錄統一靜態發布

- 修改前穩定版本已標記為 `leadership-hub-before-unified-catalog-2026-09-11`。
- 目錄現在在部署時一次產生完整文章清單；讀者瀏覽不再呼叫 `published.js` 補入雲端文章，因此不會先看到 18 篇再跳出第 19 篇。
- 雲端 API 保留給作者工作台的草稿保存與發布流程；新增或確認文章後需重新建置與部署。

## 2026-09-12：工作台口播音訊保存修正

- `audio_data` 的 Base64 MP3 只送雲端保存，不再寫入瀏覽器 `leadershipHub:articleAdmin:records`，避免超過 localStorage 容量。
- 工作台音訊播放器仍使用記憶體中的資料立即試聽；重新載入時由雲端草稿資料恢復。

## 2026-09-10：ARTICLE 19 舊草稿遷移與正式發布

- 「好教練不急著要答案」的正式來源已建立於 `content/articles/article_19/`。
- 正式頁面為 `Article_Learning_Article19.html`，使用 `assets/article-19-coaching-reflection-illustration.png`。
- 已還原舊雲端文章全文及 Markdown 表格；建置後表格會輸出為 `.reading-table` HTML。
- `list-published` 會隱藏已遷移的舊 ID `draft_1788935242062`，避免目錄出現 ARTICLE 21 或重複文章。
- 未來發布只能配發 `article_N`，N 取現有正式文章最大編號加一；不可從 draft ID 或建立時間推算。
- ARTICLE 19 摘要音檔為 `audio_summaries/article_19_summary.mp3`，口播稿為同名 `.txt`，使用本專案 `.env` 固定的 `MINIMAX_VOICE_ID`。
- ARTICLE 19 已發布至雲端正式資料，公開頁為 `https://one-page-leadership-hub.netlify.app/article?id=article_19`；目錄、PNG 主圖與摘要播放器已完成驗證。
- 2026-09-11：摘要播放器依使用者確認移出正式文章內文；目錄卡片仍保留「播放摘要」。共用渲染器與預覽同步，不影響文章音檔 API。

## 2026-09-08 定版基準

- 使用者確認目前版本為定版，程式內容基準為 `c0370e0`，完整定版以標籤 `leadership-hub-final-2026-09-08` 為準。
- GitHub `main` 與 Netlify production 已同步；正式網站為 https://one-page-leadership-hub.netlify.app。

## 2026-09-10：動態發布模板分支

- 分支：`codex/dynamic-publishing-template`；ARTICLE 19 發布修正分支 `codex/preview-article19` 已合併至 `main`。
- 舊 ARTICLE 19 已移除，ARTICLE 01–18 保留不變。
- 預覽與正式雲端文章共用 `netlify/functions/lib/render-article.mjs`；新文章從 ARTICLE 19 起以雲端動態頁發布，音檔使用獨立 API。
- 已完成本機驗證，合併至 `main` 並推送 GitHub；2026-09-10 已部署至 Netlify production。
- ARTICLE 17 主圖為 `assets/article-17-from-answers-to-learning-illustration-v2.png`，採 ARTICLE 15／16 的細緻水彩墨線風格。
- 目錄中的已發布文章固定連到正式 HTML；雲端資料只更新文章卡內容。
- 已發布文章的外部影音網址由工作台同步至雲端，正式文章頁透過 `assets/article-live-video.js` 套用最新版網址。
- 後續所有修改先由 `main` 建立 `codex/` 分支，驗證後才合併與部署。
- 2026-09-10 新增快問快答品質門檻：生成入口負責產生與驗證內容，預覽器只渲染；API 若首次回傳不完整會只重生該區塊。工作台可人工編輯三題、選項與回饋，發布 API 也會拒絕不完整的進階文章。
- 2026-09-10 修正快問快答顯示：雲端資料若以 JSON 字串或舊版欄位格式保存，預覽與正式頁會先正規化後顯示，避免題目區塊因資料型態不一致而消失。23 項測試通過，已部署。
- 2026-09-10 工作台改為草稿模式：移除預覽與發布按鈕，並移除快問快答／自我整理編輯區；保留草稿保存與 AI 內容編輯，正式預覽與發布由 Codex 使用同一份雲端資料完成。相關資料由正式流程建立與檢查。
- 2026-09-10 Netlify 已連接 GitHub `Linchatgpt/one-page-leadership-hub` 的 `main` 分支；建置指令為 `python3 scripts/build_article_hub.py`，函式目錄為 `netlify/functions`，後續推送 `main` 會自動部署。
- 2026-09-10 工作台狀態規則：已發布文章可按「轉為草稿」；任何內容保存、AI 生成或音訊處理都會先轉為草稿，避免直接覆蓋正式文章。草稿仍可由工作台刪除並同步刪除雲端資料。
- 發布編號規則：草稿不得沿用 `draft_<timestamp>`；發布 API 會依正式文章最高編號分配下一個 `article_N`，並寫入對應的 `Article_Learning_ArticleN.html` 路徑。既有錯誤草稿需遷移，不可只改畫面文字。
- 2026-09-08 已確認五個未納管的舊測試圖片沒有任何專案引用，並移至 macOS 垃圾桶；目前 Git 工作目錄乾淨。

## 首頁音檔

首頁顯示「播放摘要」文字與原生 audio controls；播放器位於文章連結之外，手機播放不會跳轉，同頁開始新摘要時會自動停止上一個摘要。音檔來源為 `audio_summaries/article_XX_summary.mp3`，由 `scripts/build_article_hub.py` 產生。

本專案的摘要音檔 Voice ID 固定，新增或重製音檔時必須沿用既定 Voice ID；不得使用 Mac 內建 `say` 或其他替代聲音，以維持全站聲音一致性。

目前固定 Voice ID 已儲存在本專案本機 `.env` 的 `MINIMAX_VOICE_ID`；MiniMax API Key 僅從本機秘密設定讀取，不放入本專案或公開檔案。

2026-09-06：正式網站目錄與作者工作台已同步；文章 18、19、20 已依使用者確認永久刪除，工作台也會隱藏這三筆舊資料。目錄維持每頁四篇、最新文章優先、編號不因封存或刪除而重排。

本專案是由文章設定檔自動產生的 One-Page Leadership Hub。來源資料位於 `content/articles/article_XX/`，不要只直接修改生成 HTML。

作者工作台入口為 `http://localhost:5200/author-admin.html`，由本專案的 `scripts/author_server.py` 提供；它只使用本專案的 localStorage 與 `.env`，不連接 One-Page Personal hub。

網頁互動設計遵循共用規範：所有按鈕都要有 hover、focus、active 與處理中／完成回饋，詳見 `/Users/wes_mini/Projects/WEB_DESIGN_GUIDELINES.md`。

目前 ARTICLE 01–10 均已依新版 One Page Hub 規格配置主題插圖；ARTICLE 04–10 的工具卡已用 Markdown inline markers 放置於相關閱讀段落後。

One Page Hub 技能已補充 SEO 必檢規則：建置器提供全域技術 SEO，每篇文章仍須在 `article.json` 個別提供搜尋意圖、SEO 標題、摘要、主要／相關關鍵詞與搜尋問題。
One Page Hub 技能與建置器也會在建置前檢查每篇文章的 `hero_image` 是否存在；缺少圖片時直接停止建置，避免生成破圖頁面。
Markdown 來源中的 `###` 小標由建置器統一轉為 `<h3>`；不得讓原始 `###` 標記直接出現在生成 HTML。

## 建置

```bash
python3 scripts/build_article_hub.py
```

### 2026-09-10 預覽與發布工作狀態

- ARTICLE 19 已由 `codex/preview-article19` 合併至 `main`，推送 GitHub 並完成 Netlify production 部署。
- 「好教練不急著要答案」已用雲端草稿資料在本機 5200 預覽；預覽已確認標題、專屬 PNG 主圖、課前三題（預設收合）、正文表格、情境案例、四題自我整理、兩個工具與 04／05 區塊均存在。
- 預覽資料暫存於瀏覽器 localStorage 的 `leadershipHub:articleAdmin:preview`，這是為了讓使用者先檢視，不會改動雲端草稿或正式文章。
- 使用者確認預覽後，已把整理後資料寫回來源、合併 `main`、推送 GitHub 並部署 Netlify。
- 防止再次發生內容稀釋：雲端草稿不得以摘要或截短正文取代完整文章；預覽資料必須以完整 `article.md` 為正文來源，並以 ARTICLE 17／18 的正式頁作為視覺與結構基準。發布前需檢查正文長度、段落標題、表格、工具卡、課前題目、自我整理、主圖、音訊與頁尾。
- 2026-09-10：共用渲染器與本機預覽已修正自我整理選項物件被直接輸出的問題；工具卡現在保留步驟與 80–120 字左右的用途說明。預覽確認無 `{text, feedback}` 原始物件字串、`[object Object]` 或重複工具卡。
- 後續每篇新文章都要先完成「ARTICLE 17／18 對齊檢查」：正文不可用摘要替代，預覽與發布必須使用共用渲染器，並逐項驗證題目、工具、表格、主圖、音訊與頁尾；未通過不得發布。

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
- 目前主目錄顯示 ARTICLE 01–09，ARTICLE 09 聚焦五步教練路徑、績效對話與責任追蹤。
- 目前主目錄顯示 ARTICLE 01–10，ARTICLE 10 聚焦教練式傾聽、介入判斷與部屬解題能力。
- 目前主目錄顯示 ARTICLE 01–11，ARTICLE 11 聚焦環境設計、降低工作錯誤與拖延，以及保留必要的績效責任。
- 目前主目錄顯示 ARTICLE 01–12，ARTICLE 12 聚焦把口頭答應轉成具體承諾、用 GROW 診斷與行動，以及在教練與績效管理間切換。
- 目前主目錄顯示 ARTICLE 01–13，ARTICLE 13 聚焦正念管理、主管注意力、情緒調節與團隊工作節奏。
- ARTICLE 13 另包含 PsyCap 的 HERO 模型、90/10 能量管理、晚上 8 點後非緊急郵件界線、彈性安排、數位輔助工具與正念管理檢核表；修改時要維持「正念落在制度，不只落在個人課程」的主線。
- ARTICLE 13 目前有三個 inline 工具欄：注意力噪音盤點卡、主管正念管理檢核表、四週正念管理試行表；不要再把四週試行流程重複寫成長篇正文。
- 主目錄文章依最新到最舊排列，每組四篇；使用「較新文章／較舊文章」切換文章組。文章卡標題採單行省略，避免長標題造成卡片高度不一致。
- 工作工具卡由建置器統一補上使用與回看說明；修改工具卡時應保留原本的步驟與文章專屬內容。
- 01 深入閱讀的 `.reading-essay` 與 `.reading-tool` 使用主欄寬度；修改 CSS 後需更新 `article-learning.css?v=YYYYMMDD` 版本參數，避免本地或瀏覽器保留舊樣式。
- 所有文章頁的 03 自我整理區塊預設收起；工具卡包含步驟與延伸說明；章節標題統一採精簡版本。
- 文章頁主內容欄明確限制最大寬度 920px，正文與工具卡最大寬度 780px；03 自我整理收起指示使用 `-`。
- 03 自我整理的互動標示比照 BEFORE YOU READ：預設收合，右側顯示「點擊展開／收起」，展開時以 `-` 表示可收回。
- 文章頁主欄與 section 皆有共用最大寬度限制，04／05 不應因文章內容而展開成全螢幕寬。
- 03 自我整理的 details 容器結構已修正；04 工作紀錄與 05 行動承諾保持在文章主欄內。
- 04 工作紀錄與 05 行動承諾使用 `max-width: 920px`，與 03 自我整理外框及文章主欄對齊。
- 目前主目錄顯示 ARTICLE 01–04；舊版被移除的原 article_01 已保留於 `content/archive/article_legacy_01/`，不會由建置器讀取。

## PWA 與手機版經驗

- PWA 已加入 `manifest.webmanifest`、`service-worker.js`、`pwa.js`、192／512／Apple touch icons 與 `PWA_PROFILE.md`；部署前需執行 `python3 scripts/check_pwa.py`。
- 安裝提示採可關閉的懸浮式設計，不使用 modal；Mac／Android 由 `beforeinstallprompt` 安裝，iPhone／iPad 明確提示點右上角分享按鈕（方框上箭頭）再選加入主畫面。
- standalone／`navigator.standalone`／`appinstalled` 用於避免從 App 模式重複顯示提示；瀏覽器分頁是否再次觸發安裝事件由瀏覽器決定。
- 目錄桌面版維持四篇一組與雙欄；手機版必須一篇一列。手機 CSS 同時寫在共用 CSS 與生成首頁的 inline style，避免只改外部 CSS 後仍被舊規則影響。
- 修改 CSS 後要更新 query-string 版本（例如 `article-learning.css?v=YYYYMMDD...`）並提高 Service Worker `CACHE_NAME`，否則手機可能持續看到舊版四格。
- 本機手機測試不能使用手機自己的 `localhost`；要用 Mac 區網 IP 加埠號，兩台裝置需在同一 Wi-Fi。完整 PWA 安裝資格仍需 HTTPS 網址。
- 最近一次 PWA／手機版部署 commit：`b15b044`；production URL：https://one-page-leadership-hub.netlify.app。
- ARTICLE 14 為白皮書頁型，不套用一般管理文章的快問快答、評估與工具卡；來源內容保留最低修改原則，PDF 五頁視覺以 `assets/article_14/page-01.png` 至 `page-05.png` 沿用，原始 PDF 可下載。
- ARTICLE 14 預覽若出現內容重複，確認不要同時顯示全文 HTML 與完整 PDF 頁面；目前以原始五頁視覺為主，避免白皮書版面混亂。

## ARTICLE 20 發布（2026-09-12）

- ARTICLE 20 已以共用正式文章模板發布，文章 ID 為 `article_20`。
- 主圖為 `assets/article-20-fact-interpretation-illustration.png`；工具卡已轉為 renderer 可辨識的結構。
- 建置器與動態發布編號基準已更新到 19，避免後續自動編號覆蓋 ARTICLE 20。

## ARTICLE 21 草稿匯入（2026-09-12）

- 原始 TXT 已保存為 `content/articles/article_21/article.md`，設定檔標記為 `draft`。
- ARTICLE 21 已完成預覽準備：顯示標題為「維持成人自我狀態」，正文仍保留完整原文。
- 已加入標準 `quick_scan` 3 題、`questions` 4 題、兩個 inline tools、表格與 `conclusion_points`；課前與自我整理均預設收合。
- 已生成 `assets/article-21-adult-ego-state-illustration.png`（1774×887 PNG）與 `audio_summaries/article_21_summary.mp3`（32 kHz MP3）。
- 本機預覽：`http://127.0.0.1:5200/preview-article21.html?preview=20260912`；預覽頁另提供口播播放器，正式文章仍依規則只在目錄卡片提供播放摘要。
- 已通過 `python3 scripts/build_article_hub.py`、`python3 -m unittest scripts/test_admin_cache.py scripts/test_dynamic_publishing.py`、`node --check assets/admin.js`，並以 Chrome 驗證無 console error。尚未發布、尚未推送或部署。
- 2026-09-12：因 Chrome 快取曾顯示舊預覽，重新以 `?preview=20260912-v2` 驗證；畫面無 `**` Markdown 符號，口播無延遲控制碼，音訊約 63 秒，主圖與表格均正常。
- 口播規則：固定開場與結尾保留，但不得把 `<#...#>` 延遲標記寫入口播稿或送進 TTS；產檔前需以純文字檢查控制碼。
- 最新預覽已依標註刪除團隊日常段落，並平衡「把主管答案延後一輪」工具卡與結語；驗證網址為 `http://127.0.0.1:5200/preview-article21.html?preview=20260912-v3`。

## ARTICLE 21 內容精煉版（2026-09-12）

- ARTICLE 21 已依 ARTICLE 17、19、20 的重複觀點重新精煉，核心改為成人自我狀態在權力不對等下如何同時保留主管責任與部屬思考權。
- 正文現保留一個跨部門案例、成人對話四步框架與兩張工具卡；自我整理題目已同步改寫，避免再次重複前文的沉默與注意力練習。
- 口播文字與 MP3 已同步更新；預覽頁重新產生為 `http://127.0.0.1:5200/preview-article21.html?preview=20260912-v4`。
- 已通過 `python3 scripts/build_article_hub.py`、`python3 -m unittest scripts/test_admin_cache.py` 與 `python3 scripts/test_article21_quality.py`。尚未發布、尚未合併 main、尚未推送或部署。

## ARTICLE 21 雲端草稿登錄（2026-09-12）

- ARTICLE 21 精煉版已寫入 Netlify 雲端草稿儲存，沿用 `article_21`，目前狀態為 `draft`；API 驗證可取得標題「維持成人自我狀態」、正文 1750 字元、2 張工具卡與 4 題自我整理。
- 雲端工作台目前仍可能看不到它，因為正式網站的前端清單容錯修正尚未部署；修正提交為 `6d5bb46`，不涉及文章發布。

## ARTICLE 21 正式發布（2026-09-12）

- ARTICLE 21 已依確認版本發布至雲端 `leadership-articles`，並刪除 `leadership-article-drafts/article_21`，雲端已驗證為已發布且含口播資料。
- 本機正式建置已納入 ARTICLE 21，產生 `Article_Learning_Article21.html` 與新版 `index.html`；目前尚未推送 GitHub 或部署 Netlify。
- 發布後網址：`https://one-page-leadership-hub.netlify.app/article?id=article_21`。

## 目錄頁手機版 QR Code 對齊（2026-09-17）

- `assets/article-learning.css` 已修正頁尾 flex 內容區的最小寬度與長網址換行，並讓 QR Code 在手機版往內容中心保留安全距離。
- `scripts/build_article_hub.py` 已更新目錄 CSS query 版本，避免手機 Service Worker／瀏覽器沿用舊版 CSS。
- 本機建置與測試通過；目前在 `main` 工作目錄有本次未提交修改，尚未推送或部署。

## ARTICLE 22 新增（2026-09-17）

- ARTICLE 22 來源位於 `content/articles/article_22/article.md` 與 `article.json`，主題為依對話狀態切換六種提問方式。
- 已加入兩張工具卡、三題課前快問快答、四題自我整理，以及主圖 `assets/article-22-six-questioning-modes-illustration.png`。
- 建置器已允許 `article_22` 出現在作者工作台資料中；本篇摘要音檔設定為停用。
- 已完成本機建置、15 項 `scripts/test_admin_cache.py` 測試與瀏覽器驗證：主圖、表格、2 張工具卡、3 題課前題目與 4 題自我整理均正常。尚未提交、推送或部署。

## 作者工作台本機草稿保存修正（2026-09-17）

- 根因是本機 `author_server.py` 沒有實作工作臺呼叫的 `/api/list-drafts`、`/api/save-draft`，所以口播生成成功後保存請求回傳 404。
- 已補上本機草稿清單、保存與刪除流程，草稿中的口播稿與 Base64 音檔會保存於 `.local_drafts/`；該目錄已加入 `.gitignore`，不會提交到 Git。
- 已通過 16 項管理工作臺測試；需要重新啟動 `PORT=5200 python3 scripts/author_server.py` 後生效。
