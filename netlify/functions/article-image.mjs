import { getStore } from '@netlify/blobs';
export default async (request) => {
  const key = new URL(request.url).searchParams.get('key') || '';
  if (!key || !/^[a-zA-Z0-9_-]+\.png$/.test(key)) return new Response('Not Found', { status: 404 });
  const image = await getStore({ name: 'leadership-article-images', consistency: 'strong' }).get(key, { type: 'arrayBuffer' });
  if (!image) return new Response('Not Found', { status: 404 });
  return new Response(image, { headers: { 'content-type': 'image/png', 'cache-control': 'public, max-age=31536000, immutable' } });
};
