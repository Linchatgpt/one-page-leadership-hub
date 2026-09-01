const images = {
  article_15: ['assets/article-15-questioning-leadership-illustration.png', '主管透過提問帶領團隊走出變革困局'],
  article_16: ['assets/article-16-coaching-judgment-illustration.png', '主管先判斷情境，再選擇合適的教練介入方式'],
  article_17: ['assets/article-17-learning-leadership-illustration.png', '主管透過提問與傾聽，帶領團隊共同學習']
};
export default async (request) => {
  if (request.method !== 'POST') return new Response(JSON.stringify({ error: '只接受 POST 請求' }), { status: 405, headers: { 'content-type': 'application/json' } });
  const payload = await request.json().catch(() => ({}));
  const id = String(payload.id || '');
  const [hero_image, hero_image_alt] = images[id] || images.article_15;
  return new Response(JSON.stringify({ hero_image, hero_image_alt: hero_image_alt || String(payload.title || '文章主圖') }), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
};
