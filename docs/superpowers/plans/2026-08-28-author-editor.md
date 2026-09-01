# Author Editor Implementation Plan

> **For agentic workers:** Execute this plan inline in the current session; subagents are disabled for this project.

**Goal:** Add an independent local author workbench to One-Page Leadership hub for manual article editing, preview, export, and project-scoped AI assistance.

**Architecture:** Keep the public learning hub as generated static HTML. Add a separate local Python HTTP server with JSON endpoints for AI processing and file export, while the browser workbench stores drafts in project-scoped localStorage and never writes credentials into public HTML.

**Tech Stack:** Existing Python build script, Python `http.server`, vanilla HTML/CSS/JavaScript, project-local `.env`, existing Markdown/JSON article source model.

**Spec:** User request: create an editor page in One-Page Leadership hub, independent from One-Page Personal hub, supporting manual entry/editing alongside existing AI editing.

## Global Constraints

- Do not read from or modify One-Page Personal hub at runtime.
- Preserve the current generated public pages and build command.
- Keep API keys local-only and ignored by Git.
- Manual edits must remain possible when AI is unavailable.
- Preview must be clearly labeled as local draft preview and must not silently publish.

### Task 1: Editor workbench UI and local draft model

**Files:**
- Create: `author-admin.html`
- Create: `assets/admin.css`
- Create: `assets/admin.js`
- Create: `preview.html`
- Create: `assets/preview.js`

- [ ] Build the article list, new article action, editable title/category/summary/body fields, save-to-localStorage, preview, export, and clear draft controls.
- [ ] Use the existing warm paper/deep green/gold visual language with responsive keyboard-accessible form controls.
- [ ] Load seeded article metadata from a generated `admin-data.js` file and keep local drafts under a project-specific key.

### Task 2: Local AI and source export server

**Files:**
- Create: `scripts/author_server.py`
- Modify: `.env.example`
- Modify: `.gitignore`

- [ ] Serve static files on the registered admin port and expose `/api/generate-learning-page` using project-local AI settings.
- [ ] Expose `/api/export-article` to validate and write confirmed Markdown/JSON source files under `content/articles/` only after an explicit export action.
- [ ] Return clear JSON errors when the API key is absent or input is invalid.

### Task 3: Build integration and project documentation

**Files:**
- Modify: `scripts/build_article_hub.py`
- Modify: `DEV_PORTS.md`
- Modify: `HANDOFF.md`
- Modify: `USER_GUIDE.md`

- [ ] Generate `admin-data.js` from current article source files without exposing secrets.
- [ ] Document separate commands for public static preview and author workbench.
- [ ] Keep the author workbench port distinct from the public site port.

### Task 4: Verification

- [ ] Run build, Python compilation, JavaScript syntax checks, and PWA checks.
- [ ] Start the author server and verify admin page, preview page, API health, and public index HTTP responses.
- [ ] Verify source project status and confirm no files under One-Page Personal hub changed.
