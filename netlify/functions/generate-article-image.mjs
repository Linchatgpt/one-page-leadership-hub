const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
export default async (request) => {
  if (request.method !== 'POST') return json(405, { error: '只接受 POST 請求' });
  const payload = await request.json().catch(() => ({}));
  const key = process.env.AI_API_KEY;
  if (!key) return json(500, { error: '正式環境尚未設定 AI_API_KEY' });
  const title = String(payload.title || '領導學習文章').trim().slice(0, 80);
  const category = String(payload.category || '領導與管理').trim().slice(0, 40);
  const prompt = `Create a refined editorial illustration for a Traditional Chinese leadership learning website. Subject: ${title}. Category: ${category}. Use warm ivory paper background, deep forest green geometric composition, muted ochre accent, restrained premium business-education editorial style, calm human-centered leadership scene, wide 3:2 composition, no words, no letters, no logos, no watermark.`;
  try {
    const response = await fetch(process.env.AI_IMAGE_API_ENDPOINT || 'https://api.openai.com/v1/images/generations', { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${key}` }, body: JSON.stringify({ model: process.env.AI_IMAGE_MODEL || 'gpt-image-1', prompt, size: '1536x1024', quality: 'medium', output_format: 'png' }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) return json(response.status, { error: data.error?.message || '主圖生成失敗' });
    const base64 = data.data?.[0]?.b64_json;
    if (!base64) return json(502, { error: '圖片服務沒有回傳 PNG' });
    return json(200, { hero_image: `data:image/png;base64,${base64}`, hero_image_alt: title });
  } catch (error) { return json(500, { error: error.message || '主圖生成失敗' }); }
};
