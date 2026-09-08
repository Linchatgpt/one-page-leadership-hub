import { getStore } from '@netlify/blobs';
export default async () => {
  const store = getStore({ name: 'leadership-article-drafts', consistency: 'strong' });
  const { blobs } = await store.list();
  const drafts = [];
  for (const blob of blobs) { const item = await store.get(blob.key, { type: 'json' }); if (item) drafts.push(item); }
  return new Response(JSON.stringify(drafts), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
};
