const esc = (value = '') => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

const text = (value, fallback = '') => {
  if (value == null || value === '') return fallback;
  if (Array.isArray(value)) return value.map((item) => text(item)).filter(Boolean).join('；');
  if (typeof value === 'object') return Object.values(value).map((item) => text(item)).filter(Boolean).join('<br><br>');
  return String(value).replace(/\\["']/g, '"').replace(/。；/g, '。').replace(/；。/g, '。');
};

function tableHtml(lines) {
  const rows = lines.filter((line) => line.includes('|')).map((line) => line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim()));
  if (rows.length < 2) return '';
  const bodyRows = rows.slice(1).filter((row) => !row.every((cell) => /^:?-{2,}:?$/.test(cell)));
  return `<div class="reading-table"><table><thead><tr>${rows[0].map((cell) => `<th>${esc(cell)}</th>`).join('')}</tr></thead><tbody>${bodyRows.map((row) => `<tr>${rows[0].map((_, index) => `<td>${esc(row[index] || '')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}

function markdownHtml(markdown, tools) {
  const lines = String(markdown || '尚未填寫文章正文').replace(/\r/g, '').split('\n');
  const out = [];
  let paragraph = [];
  let list = [];
  const flush = () => {
    if (paragraph.length) out.push(`<p>${paragraph.map((line) => esc(line)).join('<br>')}</p>`);
    paragraph = [];
    if (list.length) out.push(`<ul>${list.map((item) => `<li>${esc(item)}</li>`).join('')}</ul>`);
    list = [];
  };
  for (let index = 0; index < lines.length;) {
    const line = lines[index].trim();
    if (!line) { flush(); index += 1; continue; }
    if (line.startsWith('|') && index + 1 < lines.length && lines[index + 1].includes('|')) {
      flush(); const table = [];
      while (index < lines.length && lines[index].trim().includes('|')) table.push(lines[index++].trim());
      out.push(tableHtml(table)); continue;
    }
    const marker = line.match(/^<!--\s*TOOL_([123])\s*-->|^__TOOL_([123])__$/i);
    if (marker) { flush(); const tool = tools[Number(marker[1] || marker[2]) - 1]; if (tool) out.push(toolHtml(tool)); index += 1; continue; }
    if (/^###\s+/.test(line)) { flush(); out.push(`<h3>${esc(line.replace(/^###\s+/, ''))}</h3>`); index += 1; continue; }
    if (/^##\s+/.test(line)) { flush(); out.push(`<h2>${esc(line.replace(/^##\s+/, ''))}</h2>`); index += 1; continue; }
    if (/^#\s+/.test(line)) { flush(); out.push(`<h2>${esc(line.replace(/^#\s+/, ''))}</h2>`); index += 1; continue; }
    if (/^-\s+/.test(line)) { if (paragraph.length) flush(); list.push(line.replace(/^-\s+/, '')); index += 1; continue; }
    paragraph.push(line.replace(/^>\s*/, '')); index += 1;
  }
  flush();
  return out.join('\n').replace(/導言｜/g, '<strong>導言｜</strong>');
}

function toolHtml(tool) {
  const title = text(tool.title, '工作工具');
  const label = text(tool.label, '工作工具');
  const steps = Array.isArray(tool.steps) ? `<p class="tool-steps"><strong>${tool.steps.map((step) => esc(text(step))).join('<br>')}</strong></p>` : '';
  const explanation = text(tool.explanation || tool.body);
  return explanation || steps ? `<aside class="reading-tool"><span class="tool-label">${esc(label)}</span><h3>${esc(title)}</h3>${steps}${explanation ? `<p>${esc(explanation)}</p>` : ''}</aside>` : '';
}

function scanHtml(items = []) {
  return items.map((item, index) => { const choices = item.options || item.choices || item.answers || []; return `<div class="scan-question"><p>${String(index + 1).padStart(2, '0')} · ${esc(text(item.question || item.prompt || item.title))}</p><div class="scan-options">${choices.map((option) => { const value = typeof option === 'string' ? { text: option } : option || {}; return `<button type="button" data-feedback="${esc(value.feedback || '')}">${esc(text(value.text || value.label || value.value))}</button>`; }).join('')}</div><p class="scan-feedback" aria-live="polite"></p></div>`; }).join('');
}

function questionsHtml(items = []) {
  return items.map((item, index) => `<fieldset class="question"><legend><span class="question-number">${index + 1}.</span> ${esc(text(item.question))}</legend><div class="assessment-options">${(item.options || []).map((option) => `<label class="assessment-option"><input type="radio" name="q${index}" value="${esc(text(option.text || option))}" data-option="${esc(text(option.text || option))}" data-key="q${index}"><span>${esc(text(option.text || option))}</span></label>`).join('')}</div><small class="question-label">學習焦點</small></fieldset>`).join('');
}

function caseHtml(value) {
  if (!value) return '';
  if (typeof value === 'object') return Object.values(value).map((item) => text(item)).filter(Boolean).map((item) => esc(item)).join('<br><br>');
  return esc(text(value));
}

export default function renderArticle(article = {}) {
  const a = { ...article };
  const number = String(a.id || 'article_19').split('_').pop();
  const title = text(a.title, '未命名文章');
  const summary = text(a.summary);
  const subtitle = text(a.subtitle, '把觀點帶回一個可觀察的工作行動');
  const category = text(a.category, '未分類');
  const tools = (Array.isArray(a.tools) ? a.tools : []).filter((tool) => tool && (tool.explanation || tool.body || (tool.steps && tool.steps.length)));
  let body = markdownHtml(a.body_markdown, tools);
  if (!/reading-tool/.test(body) && tools.length) body += tools.map(toolHtml).join('');
  const conclusion = Array.isArray(a.conclusion_points) ? a.conclusion_points.filter(Boolean) : [];
  if (conclusion.length) body += `<div class="reading-summary"><span class="summary-label">深入閱讀收束</span><h2>總結提要</h2><ul>${conclusion.map((item) => `<li>${esc(text(item))}</li>`).join('')}</ul></div>`;
  const image = text(a.hero_image);
  const audio = text(a.audio_asset || a.audio_url);
  const caseContent = caseHtml(a.case);
  const imageHtml = image ? `<figure class="article-hero-visual"><img src="${esc(image)}" alt="${esc(text(a.hero_image_alt, title))}"></figure>` : '';
  const audioHtml = audio ? `<div class="module-audio"><span class="audio-label">播放摘要</span><audio controls preload="none" src="${esc(audio)}" aria-label="播放文章 ${number} 摘要"></audio></div>` : '';
  const videoHtml = a.video_url ? `<aside class="external-video"><small class="kicker">延伸影音</small><a href="${esc(a.video_url)}" target="_blank" rel="noopener">在 YouTube 觀看影片 →</a></aside>` : '';
  const orientation = (Array.isArray(a.orientation) ? a.orientation : []).map((item) => `<li>${esc(text(item))}</li>`).join('');
  const selfReview = (a.questions || []).length ? `<details class="self-review"><summary><span><small>SELF REVIEW</small><strong>自我整理（${a.questions.length}題）</strong></span><b>點擊展開／收起</b></summary><div class="self-review-body"><div class="assess">${questionsHtml(a.questions)}</div><div class="assessment-actions"><button class="button" id="submitAssessment">整理我的學習焦點</button><button class="clear-button" id="clearAssessment">清除自我整理</button></div><p id="assessmentMessage" class="assessment-message" aria-live="polite"></p><div id="assessmentResult" class="result"></div></div></details>` : '';
  const clientArticle = { ...a, body_markdown: String(a.body_markdown || '').replace(/<!--\s*TOOL_[123]\s*-->|__TOOL_[123]__/gi, '') };
  return `<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(title)}｜精萃領導™學習中心</title><meta name="description" content="${esc(summary)}"><link rel="stylesheet" href="/assets/article-learning.css?v=dynamic-article-1"><link rel="manifest" href="/manifest.webmanifest"></head><body><div class="top article-top"><a class="brand" href="/" aria-label="返回精萃領導TM學習中心"><i>LE</i> 精萃領導™學習中心</a><span class="save" id="saveStatus">已發布</span></div><div class="layout"><aside class="side"><small>ARTICLE ${esc(number)}</small><h2>${esc(title)}</h2><nav aria-label="文章段落"><a href="#s1">01 深入閱讀</a><a href="#s2">02 情境案例</a><a href="#s3">03 自我整理</a><a href="#s4">04 工作紀錄</a><a href="#s5">05 行動承諾</a></nav></aside><main><section class="hero"><small class="kicker">${esc(category)} · ${esc(a.reading_minutes || 8)} MIN READ</small><h1>${esc(title)}</h1><h2 class="hero-subtitle">${esc(subtitle)}</h2><p class="lead">${esc(summary)}</p><div class="dark"><small>開始前，先想一想</small><h3>${esc(text(a.start_prompt, '讀完這篇文章後，你想帶回哪一個工作情境？'))}</h3><label>我的第一個念頭<textarea id="startPrompt" data-key="startPrompt" rows="2" placeholder="寫下一句就好"></textarea></label></div></section>${imageHtml}<section id="s1"><div class="head"><small class="kicker">01 深入閱讀</small><h2>實用概念</h2><p>把文章中的觀點轉成你今天能辨認的工作訊號。</p></div>${orientation ? `<div class="reading-brief"><span class="brief-label">ONE-MINUTE ORIENTATION</span><h3>閱讀時，請留意四個轉折</h3><ul>${orientation}</ul></div>` : ''}${(a.quick_scan || []).length ? `<details class="quick-scan" open><summary><span><small>BEFORE YOU READ</small><strong>課前情境快問快答（${a.quick_scan.length}題）</strong></span><b>點擊展開／收起</b></summary><div class="quick-scan-body"><p class="scan-intro">請依直覺選擇。這不是測驗，沒有標準答案。</p>${scanHtml(a.quick_scan)}</div></details>` : ''}<article class="reading-essay">${body}${videoHtml}</article>${audioHtml}</section><section id="s2"><div class="head"><small class="kicker">02 情境案例</small><h2>帶回現場</h2><p>${caseContent}</p></div><textarea id="caseNote" data-key="caseNote" rows="6" placeholder="寫下你的處理方式"></textarea></section><section id="s3"><div class="head"><small class="kicker">03 自我整理</small><h2>整理焦點</h2><p>把剛才的直覺整理成一個工作焦點。沒有標準答案，請選最接近你目前狀態的句子。</p></div>${selfReview}</section><section id="s4"><div class="head"><small class="kicker">04 工作紀錄</small><h2>留下觀察</h2></div><div class="simple-record"><label>我在工作中注意到……<textarea id="observation" data-key="observation" rows="4"></textarea></label><label>給自己的話<textarea id="personalNote" data-key="personalNote" rows="3"></textarea></label></div></section><section id="s5"><div class="head"><small class="kicker">05 行動承諾</small><h2>我的實踐</h2><div class="experiment-focus" id="focusTip">先完成自我整理，這裡會顯示你的發展焦點。</div></div><div class="simple-record action-commitment"><label>我會試做……<textarea id="commitment" data-key="commitment" rows="4"></textarea></label><label class="action-date">預計日期 <input id="commitmentDate" data-key="commitmentDate" type="date"></label></div></section><footer class="site-footer article-footer"><div><strong>精萃領導™學習中心</strong><a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a></div><img src="/assets/line-qr.png" alt="加入 LINE 諮詢領導課程"></footer></main></div><script>window.ARTICLE_DATA=${JSON.stringify(clientArticle)};</script><script src="/assets/article-learning.js"></script><script src="/assets/article-live-video.js" defer></script></body></html>`;
}
