import { getStore } from '@netlify/blobs';

export default async function () {
  const migratedLegacyIds = new Set(['draft_1788935242062']);
  const store = getStore({ name: 'leadership-articles', consistency: 'strong' });
  const items = await store.list();
  const articles = [];
  for (const blob of items.blobs || []) {
    const article = await store.get(blob.key, { type: 'json' });
    if (article?.status === 'published' && article.title && article.body_markdown && !migratedLegacyIds.has(article.id)) articles.push(article);
  }
  articles.sort((a, b) => new Date(a.published_at || 0) - new Date(b.published_at || 0));
  const highest = articles.reduce((max, article) => Math.max(max, Number(String(article.id).match(/article_(\d+)$/)?.[1] || 0)), 19);
  const legacy = articles.filter((article) => !/^article_\d+$/.test(String(article.id)));
  const result = articles.map((article, index) => {
    const match = String(article.id).match(/^article_(\d+)$/);
    const number = match ? Number(match[1]) : highest + legacy.indexOf(article) + 1;
    return { ...article, number, page: match ? (article.page || `Article_Learning_Article${number}.html`) : undefined };
  });
  return new Response(JSON.stringify(result), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
}
