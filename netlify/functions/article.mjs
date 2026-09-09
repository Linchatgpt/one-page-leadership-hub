import { getStore } from '@netlify/blobs';
import renderArticle from './lib/render-article.mjs';

export default async function (request) {
  const id = new URL(request.url).searchParams.get('id') || '';
  const article = await getStore({ name: 'leadership-articles', consistency: 'strong' }).get(id, { type: 'json' });
  if (!article || article.status !== 'published') return new Response('Not Found', { status: 404 });
  return new Response(renderArticle(article), {
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' }
  });
}
