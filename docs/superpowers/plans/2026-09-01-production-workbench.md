# Production Workbench Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with verification checkpoints.

**Goal:** Make the Leadership article workbench usable from the deployed Netlify URL, including AI article generation, audio-script generation, summary audio, preview, and publishing.

**Architecture:** Keep the public site static, move request/response API routes into Netlify Functions, and store published article records in Netlify Blobs so serverless invocations do not depend on the local filesystem. The browser keeps local drafts, while publish writes the canonical record and rebuilds are handled by a deploy-safe data path.

**Tech Stack:** Netlify Functions, Node.js, OpenAI-compatible chat completion API, MiniMax TTS API, Netlify Blobs, existing static HTML/CSS/JavaScript.

**Spec:** Existing project behavior documented in `HANDOFF.md`, `USER_GUIDE.md`, and `scripts/author_server.py`.

## Global Constraints

- Keep the fixed MiniMax Voice ID `moss_audio_39eb1dad-2537-11f1-9471-ba789c2c93f8`.
- Never commit `.env` or expose API keys to browser JavaScript.
- Preserve the distinction between the public directory and the author workbench.
- Verify the deployed URL end-to-end before reporting completion.

### Task 1: Serverless API foundation

**Files:**
- Create: `netlify/functions/api.mjs`
- Modify: `netlify.toml`
- Test: `scripts/test_deployed_api.py`

- [ ] Add a single Netlify Function handling the workbench API paths and returning the existing JSON contracts.
- [ ] Move AI and MiniMax calls to server-side environment variables.
- [ ] Configure `/api/*` redirects to the function and set the functions directory.
- [ ] Test health, missing-key, and malformed-request responses locally with Netlify dev.

### Task 2: Serverless article persistence and publishing

**Files:**
- Modify: `netlify/functions/api.mjs`
- Modify: `assets/admin.js`
- Test: `scripts/test_deployed_api.py`

- [ ] Store published article JSON and Markdown in Netlify Blobs under stable article IDs.
- [ ] Return publish results without relying on writes to the deployed filesystem.
- [ ] Keep local filesystem publishing behavior available for the local Python server.
- [ ] Verify duplicate publish updates the existing article instead of creating a second record.

### Task 3: Production configuration and deployment verification

**Files:**
- Modify: `netlify.toml`
- Modify: `.env.example`
- Create: `docs/PRODUCTION_WORKBENCH.md`

- [ ] Set Netlify environment variables from the existing local configuration without committing secrets.
- [ ] Build and deploy production.
- [ ] Verify directory, workbench, AI generation, audio-script generation, and preview through the production URL.
- [ ] Record the deployed URL, Git commit, and verification results.

