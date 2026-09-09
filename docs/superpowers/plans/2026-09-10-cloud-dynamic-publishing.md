# 雲端動態文章發布 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 工作台發布的新文章直接使用完整標準模板並即時出現在目錄，同時 ARTICLE 01–18 完全不變。

**Architecture:** ARTICLE 01–18 保留現有靜態頁面。新文章從 ARTICLE 19 起儲存在 Netlify Blobs，由共用 JavaScript 渲染器供預覽與 `/article?id=...` 正式頁使用；首頁只加入動態雲端文章。

**Tech Stack:** 原生 HTML/CSS/JavaScript、Python 3.13、Netlify Functions、Netlify Blobs、Python unittest、Chrome。

**Spec:** `docs/superpowers/specs/2026-09-10-cloud-dynamic-publishing-design.md`

## Global Constraints

- ARTICLE 01–18 的來源檔與生成頁必須保持逐位元一致，以 SHA-256 驗證。
- 移除 ARTICLE 19 的來源、生成頁、主圖與摘要音檔；下一篇工作台文章取得 `article_19`。
- 預覽與正式文章共用同一渲染器。
- 沒有主圖時不輸出圖片區塊，不借用其他文章圖片。
- 已發布文章編輯沿用原本 `article_N`，不可建立第二筆。
- 不修改 `author-admin.html` 現有未提交的使用者變更。
- 未經使用者明確要求，不合併 `main`、不推送 GitHub、不部署 Netlify。

---

### Task 1: 移除 ARTICLE 19 並建立凍結基準

**Files:** Delete `content/articles/article_19/*`, `Article_Learning_Article19.html`, ARTICLE 19 image/audio; modify generated `index.html`, `TASK.md`, `HANDOFF.md`; test `scripts/test_admin_cache.py`.

- [ ] Record SHA-256 for all ARTICLE 01–18 source and generated files.
- [ ] Confirm the explicit ARTICLE 19 files exist, then delete only those files and rebuild.
- [ ] Add a regression test that no source folder or generated page has ARTICLE 19 and all remaining article IDs are at most 18.
- [ ] Recompare both SHA-256 lists; any difference in ARTICLE 01–18 stops the task.
- [ ] Commit only the deletion, generated index, test, and documentation.

Commands:

```bash
find content/articles -path '*/article_*/*' ! -path '*/article_19/*' -type f -print0 | sort -z | xargs -0 shasum -a 256 > /tmp/leadership_articles_01_18_before.sha256
find . -maxdepth 1 -type f -name 'Article_Learning_Article*.html' ! -name 'Article_Learning_Article19.html' -print0 | sort -z | xargs -0 shasum -a 256 > /tmp/leadership_pages_01_18_before.sha256
python3 scripts/build_article_hub.py
```

### Task 2: 建立共用動態文章渲染器

**Files:** Create `netlify/functions/lib/render-article.mjs`; modify `netlify/functions/render-preview.mjs` and `netlify/functions/article.mjs`; test `scripts/test_dynamic_publishing.py`.

- [ ] Write a failing test requiring the standard sections, exactly four self-reflection questions, HTML tables, tool placement, and omission of the hero figure when `hero_image` is empty.
- [ ] Implement `escapeHtml`, `renderMarkdown`, `renderQuestions`, `renderTools`, `renderAudio`, and `renderArticle(article, { mode })`.
- [ ] Make preview and published dynamic article routes call exactly the same renderer.
- [ ] Escape all user/AI content; recognize `##`, `###`, paragraphs, lists, pipe tables, and inline tool markers.
- [ ] Run targeted tests and `node --check` for all changed JavaScript, then commit this task.

### Task 3: 讓發布與目錄即時使用雲端文章

**Files:** Modify `netlify/functions/api.mjs`, `netlify/functions/list-published.mjs`, `assets/published.js`; extend `scripts/test_dynamic_publishing.py`.

- [ ] Add a failing test for `STATIC_ARTICLE_MAX = 18`, stable same-ID edits, no duplicate cards, and dynamic `/article?id=article_N` links.
- [ ] Validate required article fields before writing; allocate the next ID from max(static 18, cloud IDs); delete a draft only after the new Blob write succeeds.
- [ ] Keep cloud records from replacing ARTICLE 01–18 static cards.
- [ ] Store audio as a separate Blob asset and expose an audio endpoint; do not return base64 audio in catalog responses.
- [ ] Render a player only when an audio asset exists; omit the image block when no hero image exists.
- [ ] Run API tests and JavaScript syntax checks, then commit this task.

### Task 4: 工作台驗證、文件與不變性檢查

**Files:** Modify `assets/admin.js` only where required; update `PRODUCT.md`, `USER_GUIDE.md`, `TASK.md`, `HANDOFF.md`; extend tests.

- [ ] Preserve the optional external-video field and do not reintroduce a hero-image field.
- [ ] Ensure incomplete article data rejects publishing while preserving the draft; buttons show processing state.
- [ ] Document static ARTICLE 01–18 protection and dynamic publishing from ARTICLE 19 onward.
- [ ] Rebuild, run all tests, run JavaScript syntax checks, and compare the ARTICLE 01–18 SHA-256 lists.
- [ ] Commit only intentional files; never stage the existing user edit in `author-admin.html`.

### Task 5: Chrome 驗證與分支交付

**Files:** Verify local workbench, preview, index, dynamic article route, and static ARTICLE 01–18 links.

- [ ] Start `python3 scripts/author_server.py` on the registered fixed port.
- [ ] Use one disposable draft to verify AI output, full preview, cloud save, publish as ARTICLE 19, directory appearance, dynamic article, and same-ID edit.
- [ ] Confirm tables, tools, four self-reflection questions, audio, and optional image behavior; then delete only the disposable test record.
- [ ] Re-run build, all tests, SHA-256 comparisons, `git diff --check`, and `git status`.
- [ ] Keep the branch unmerged until the user explicitly requests deployment; unchanged `main` is the rollback point.
