# 專案協作規則

- 開始修改前先讀取 `PRODUCT.md`、`TASK.md`、`HANDOFF.md` 與 `USER_GUIDE.md`。
- 先執行 `git status` 與 `git diff`，不要覆蓋未納管或不相關的使用者檔案。
- 定版基準為 Git tag `leadership-hub-final-2026-09-08`；後續修改一律從 `main` 建立 `codex/` 分支。
- 文章來源以 `content/articles/article_XX/article.json` 與 `article.md` 為準，不要只修改生成後的 HTML。
- 本專案不得與 `One-Page Personal hub` 共用文章、草稿、環境變數或部署設定。
- 修改後執行 `python3 scripts/build_article_hub.py` 與 `python3 -m unittest scripts/test_admin_cache.py`。
- 只有使用者明確要求發布時，才合併至 `main`、推送 GitHub並部署 Netlify。
- 完成前更新 `TASK.md` 與 `HANDOFF.md`；產品行為改變時同步更新 `PRODUCT.md` 與 `USER_GUIDE.md`。

