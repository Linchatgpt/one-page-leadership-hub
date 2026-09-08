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


if __name__ == '__main__':
    unittest.main()
