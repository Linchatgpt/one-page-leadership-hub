import renderArticle from './lib/render-article.mjs';

export default async (request) => {
  if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  const article = await request.json().catch(() => ({}));
  return new Response(renderArticle({ ...article, status: 'preview' }), {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' }
  });
};
