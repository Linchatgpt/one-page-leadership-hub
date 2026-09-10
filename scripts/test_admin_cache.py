from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AdminCachePolicyTest(unittest.TestCase):
    def test_service_worker_excludes_authoring_pages(self):
        source = (ROOT / 'service-worker.js').read_text()
        self.assertIn("'/author-admin.html'", source)
        self.assertIn("'/preview.html'", source)

    def test_local_server_disables_cache_for_authoring_pages(self):
        source = (ROOT / 'scripts' / 'author_server.py').read_text()
        self.assertIn("Cache-Control', 'no-store", source)

    def test_admin_script_only_adds_optional_video_field(self):
        source = (ROOT / 'assets' / 'admin.js').read_text()
        self.assertNotIn('文章主圖路徑', source)
        self.assertIn('外部影音檔網址（選填）', source)

    def test_local_publish_always_generates_a_fresh_image(self):
        source = (ROOT / 'scripts' / 'author_server.py').read_text()
        self.assertNotIn("if not str(article.get('hero_image', '')).strip():", source)
        self.assertIn("/api/generate-article-image", source)

    def test_published_article_builder_embeds_youtube_video(self):
        source = (ROOT / 'scripts' / 'build_article_hub.py').read_text()
        self.assertIn('def video_html', source)
        built = (ROOT / 'Article_Learning_Article18.html').read_text()
        self.assertIn('youtube.com/embed/Pq-JIYXm3Pc', built)

    def test_directory_uses_article_id_as_unique_key(self):
        builder = (ROOT / 'scripts' / 'build_article_hub.py').read_text()
        published = (ROOT / 'assets' / 'published.js').read_text()
        self.assertIn('data-article-id=', builder)
        self.assertIn("querySelector('[data-article-id=", published)

    def test_published_card_preserves_static_article_page(self):
        published = (ROOT / 'assets' / 'published.js').read_text()
        self.assertIn("article.page", published)
        self.assertNotIn("href=\"/article?id=", published)

    def test_directory_loads_static_link_fix_without_stale_cache(self):
        directory = (ROOT / 'index.html').read_text()
        self.assertIn('assets/published.js?v=20260908-static-article-links', directory)

    def test_workbench_cloud_article_overrides_embedded_copy(self):
        admin = (ROOT / 'assets' / 'admin.js').read_text()
        self.assertIn('Object.assign(existing,item)', admin)

    def test_saving_published_article_updates_same_cloud_record(self):
        admin = (ROOT / 'assets' / 'admin.js').read_text()
        api = (ROOT / 'netlify' / 'functions' / 'api.mjs').read_text()
        self.assertIn("fetch('/api/save-published'", admin)
        self.assertIn("path === '/save-published'", api)

    def test_published_article_autosave_uses_cloud_sync(self):
        admin = (ROOT / 'assets' / 'admin.js').read_text()
        self.assertIn('function syncArticle(a)', admin)
        self.assertGreaterEqual(admin.count('syncArticle(a)'), 3)

    def test_workbench_loads_video_sync_fix_without_stale_cache(self):
        workbench = (ROOT / 'author-admin.html').read_text()
        self.assertIn('assets/admin.js?v=20260910-quick-scan-quality', workbench)
        self.assertIn('assets/admin.css?v=20260910-quick-scan-quality', workbench)

    def test_article_page_refreshes_external_video_from_cloud(self):
        article_script = ''.join(path.read_text() for path in [
            ROOT / 'assets' / 'article-learning.js',
            ROOT / 'assets' / 'article-live-video.js',
        ] if path.exists())
        self.assertIn("fetch('/api/list-published'", article_script)
        self.assertIn('syncExternalVideo', article_script)

    def test_static_baseline_articles_remain_available(self):
        article_ids = sorted(
            path.parent.name
            for path in (ROOT / 'content' / 'articles').glob('article_*/article.json')
            if path.parent.name != 'article_19'
        )
        self.assertEqual(article_ids, [f'article_{index:02d}' for index in range(1, 19)])


if __name__ == '__main__':
    unittest.main()
