import { getStore } from '@netlify/blobs';

export default async function (request) {
  const id = new URL(request.url).searchParams.get('id') || '';
  const article = await getStore({ name: 'leadership-articles', consistency: 'strong' }).get(id, { type: 'json' });
  if (!article || article.status !== 'published' || !article.audio_data) return new Response('Not Found', { status: 404 });
  const base64 = String(article.audio_data).replace(/^data:audio\/mpeg;base64,/, '');
  return new Response(Buffer.from(base64, 'base64'), {
    headers: { 'content-type': 'audio/mpeg', 'cache-control': 'public,max-age=31536000,immutable' }
  });
}
