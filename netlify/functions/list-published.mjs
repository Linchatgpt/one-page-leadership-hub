import { getStore } from '@netlify/blobs';

export default async function () {
  const store = getStore({ name: 'leadership-articles', consistency: 'strong' });
  const items = await store.list();
  const articles = [];
  for (const blob of items.blobs || []) {
    const article = await store.get(blob.key, { type: 'json' });
    if (article?.status === 'published' && article.title && article.body_markdown) articles.push(article);
  }
  articles.sort((a, b) => new Date(a.published_at || 0) - new Date(b.published_at || 0));
  const highest = articles.reduce((max, article) => Math.max(max, Number(String(article.id).match(/article_(\d+)$/)?.[1] || 0)), 17);
  const result = articles.map((article, index) => ({ id: article.id, number: Number(String(article.id).match(/article_(\d+)$/)?.[1] || highest + index + 1), title: article.title, subtitle: article.subtitle, summary: article.summary, category: article.category, reading_minutes: article.reading_minutes, hero_image: article.hero_image, audio_data: article.audio_data || '' }));
  return new Response(JSON.stringify(result), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });
}
