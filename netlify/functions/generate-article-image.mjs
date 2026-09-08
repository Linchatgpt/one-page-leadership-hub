import { getStore } from '@netlify/blobs';
const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
export default async (request) => {
  if (request.method !== 'POST') return json(405, { error: '只接受 POST 請求' });
  const payload = await request.json().catch(() => ({}));
  const key = process.env.AI_API_KEY;
  if (!key) return json(500, { error: '正式環境尚未設定 AI_API_KEY' });
  const title = String(payload.title || '領導學習文章').trim().slice(0, 80);
  const category = String(payload.category || '領導與管理').trim().slice(0, 40);
  const variants = ['a small cross-functional group around a table, viewed from a slightly elevated angle', 'a one-to-one coaching conversation with two people in profile, with observers in the background', 'a standing workshop with people arranging cards and diagrams on a wall', 'a quiet reflective scene with one facilitator and several colleagues taking notes', 'a broad team discussion in a bright room, with the main speaker off-center', 'a close conversational moment between two colleagues, with layered group activity behind them'];
  const seed = [...title].reduce((sum, char) => sum + char.codePointAt(0), 0) + String(payload.id || '').length;
  const sceneVariation = variants[seed % variants.length];
  const prompt = `Create a new wide banner editorial illustration for a Traditional Chinese leadership learning website. Subject: ${title}. Category: ${category}. Scene variation: ${sceneVariation}. The final artwork must be a long horizontal rectangular page-header composition, approximately 2:1, with important people and objects kept inside the central safe area so the image can be displayed as a consistent wide banner without losing the subject. Match the established article-15-to-17 visual language: hand-painted watercolor and gouache editorial illustration, warm textured ivory paper, muted olive and deep forest green, ochre gold and restrained terracotta accents, natural expressive people in a real workplace conversation or collaborative learning scene, thoughtful human-centered leadership atmosphere, visible paper grain and soft brush edges, balanced wide landscape composition with layered depth, premium quiet magazine style. Keep the same visual identity but deliberately vary the people, age, clothing, camera angle, gestures, room layout, plants, window or mountain elements, and table objects from other articles. Create a new scene specifically for this article. No text, no letters, no numbers, no logos, no watermark, no gradients, no glossy 3D, no photorealism, no generic corporate stock-photo look.`;
  try {
    const response = await fetch(process.env.AI_IMAGE_API_ENDPOINT || 'https://api.openai.com/v1/images/generations', { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${key}` }, body: JSON.stringify({ model: process.env.AI_IMAGE_MODEL || 'gpt-image-1', prompt, size: '1536x1024', quality: 'medium', output_format: 'png' }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) return json(response.status, { error: data.error?.message || '主圖生成失敗' });
    const base64 = data.data?.[0]?.b64_json;
    if (!base64) return json(502, { error: '圖片服務沒有回傳 PNG' });
    const id = String(payload.id || `draft_${Date.now()}`).replace(/[^a-zA-Z0-9_-]/g, '-');
    const keyName = `${id}-${Date.now()}.png`;
    await getStore({ name: 'leadership-article-images', consistency: 'strong' }).set(keyName, Buffer.from(base64, 'base64'), { metadata: { contentType: 'image/png' } });
    return json(200, { hero_image: `/api/article-image?key=${encodeURIComponent(keyName)}`, hero_image_alt: title });
  } catch (error) { return json(500, { error: error.message || '主圖生成失敗' }); }
};
