import { getStore } from '@netlify/blobs';

const json = (statusCode, body) => new Response(JSON.stringify(body), { status: statusCode, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
const bodyOf = async (event) => { try { if (typeof event.json === 'function') return await event.json(); if (typeof Request !== 'undefined' && event instanceof Request) return await event.json(); return typeof event.body === 'string' ? JSON.parse(event.body || '{}') : (event.body || event.payload || {}); } catch { throw new Error('請求格式不是有效 JSON'); } };
const clean = (value) => typeof value === 'string' ? value.replace(/[\*#＊＃]/g, '') : value;
const store = () => getStore({ name: 'leadership-articles', consistency: 'strong' });

async function chat(system, user, max_tokens = 3000, asJson = true) {
  const key = process.env.AI_API_KEY;
  if (!key) throw new Error('正式環境尚未設定 AI_API_KEY');
  const request = { model: process.env.AI_MODEL || 'gpt-5.6-luna', reasoning_effort: process.env.AI_REASONING_EFFORT || 'low', messages: [{ role: 'system', content: system }, { role: 'user', content: user }], max_completion_tokens: max_tokens };
  if (asJson) request.response_format = { type: 'json_object' };
  const response = await fetch(process.env.AI_API_ENDPOINT || 'https://api.openai.com/v1/chat/completions', { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${key}` }, body: JSON.stringify(request) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error?.message || 'AI 請求失敗');
  const content = data.choices?.[0]?.message?.content || '';
  return asJson ? JSON.parse(content || '{}') : content;
}

async function generateArticle(payload) {
  const system = '你是繁體中文管理學習內容編輯。只回傳 JSON，不要 Markdown code fence。請產生 title（12個中文字以內）、subtitle、category、reading_minutes（整數）、summary（首頁方格用，1至2句）、start_prompt、orientation（4個字串）、quick_scan（3個物件）、body_markdown、case、questions（4個物件）、focus_tips、tools（1至2個物件）。正文使用 Markdown ## 小標題與標準表格；工具標記 <!-- TOOL_1 -->、<!-- TOOL_2 --> 必須放在最相關正文段落之後且不可集中在文末。不要輸出 JSON 物件到正文。';
  const result = await chat(system, JSON.stringify({ title: clean(payload.title || ''), category: clean(payload.category || ''), source_text: clean(payload.source_text || '') }), 8000);
  result.title = String(result.title || '').replace(/\s+/g, '').split(/[：:，,。！？!?]/, 1)[0].slice(0, 12);
  result.body_markdown = String(result.body_markdown || '').replace(/^\s*>\s?/gm, '').replace(/\n{3,}/g, '\n\n');
  return result;
}

async function audioScript(payload) {
  const system = '你是繁體中文音訊編輯。只回傳 JSON，欄位只有 audio_script。根據文章寫約200至220個中文字的口播核心內容，固定開場與結尾會由系統加入，因此不要寫開場、結尾、標題、引號、Module編號、XML或時間控制符號。';
  const raw = await chat(system, `文章標題：${payload.title || ''}\n文章正文：\n${String(payload.body_markdown || '').slice(0, 12000)}`, 600, false);
  let result = raw;
  if (typeof raw === 'string') { try { result = JSON.parse(raw); } catch { result = { audio_script: raw }; } }
  result.audio_script = String(result.audio_script || result.content || result.text || '').replace(/<#[^>]+#>|\bModule\s+\d+\s*[,，]?/gi, '').replace(/[\*#＊＃]/g, '').trim();
  if (!result.audio_script) throw new Error('AI 沒有回傳有效的口播稿');
  return result;
}

async function summaryAudio(payload) {
  const key = process.env.MINIMAX_API_KEY;
  if (!key) throw new Error('正式環境尚未設定 MINIMAX_API_KEY');
  const text = String(payload.summary ?? payload.audio_script ?? payload.text ?? '').replace(/<#[^>]+#>|\bModule\s+\d+\s*[,，]?/gi, '').replace(/[\*#＊＃]/g, '').trim();
  if (!text) throw new Error('口播稿內容為空');
  const response = await fetch(process.env.MINIMAX_API_ENDPOINT || 'https://api.minimax.io/v1/t2a_v2', { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${key}` }, body: JSON.stringify({ model: process.env.MINIMAX_MODEL || 'speech-2.8-hd', text, stream: false, language_boost: 'auto', output_format: 'hex', voice_setting: { voice_id: process.env.MINIMAX_VOICE_ID || 'moss_audio_39eb1dad-2537-11f1-9471-ba789c2c93f8', speed: 1, vol: 1, pitch: 0 }, audio_setting: { sample_rate: 32000, bitrate: 128000, format: 'mp3', channel: 1 } }) });
  const data = await response.json();
  if (!response.ok || data.base_resp?.status_code) throw new Error(data.base_resp?.status_msg || 'MiniMax 音訊產生失敗');
  return { audio_data: `data:audio/mpeg;base64,${Buffer.from(data.data?.audio || '', 'hex').toString('base64')}` };
}

export default async (event, context, forcedPath = '') => {
  try {
    const requestPath = forcedPath || (event.path || new URL(event.url || event.rawUrl || 'http://localhost/.netlify/functions/api').pathname);
    const path = event.queryStringParameters?.route ? `/${event.queryStringParameters.route.replace(/^\//, '')}` : (requestPath.replace(/^.*\/\.netlify\/functions\/api/, '').replace(/^\/api/, '') || '/');
    const payload = await bodyOf(event);
    const method = event.method || event.httpMethod || event.requestContext?.http?.method || event.request?.method || (path === '/health' ? 'GET' : 'POST');
    if (method === 'GET' && path === '/health') return json(200, { ok: true, project: 'one-page-leadership-hub', runtime: 'netlify-functions' });
    if (method !== 'POST') return json(405, { error: '只接受 POST 請求' });
    if (path === '/generate-learning-page') return json(200, await generateArticle(payload));
    if (path === '/generate-audio-script') return json(200, await audioScript(payload));
    if (path === '/generate-summary-audio') return json(200, await summaryAudio(payload));
    if (path === '/publish-article') { const id = String(payload.id || `article_${Date.now()}`).replace(/[^a-zA-Z0-9_-]/g, '-'); await store().setJSON(id, { ...payload, id, status: 'published', published_at: new Date().toISOString() }); return json(200, { ok: true, id, page: `Article_Learning_${id.replace('article_', 'Article')}.html` }); }
    return json(404, { error: '找不到 API 路徑', path });
  } catch (error) { return json(500, { error: error.message || '伺服器錯誤' }); }
};
