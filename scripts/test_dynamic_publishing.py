import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / 'netlify' / 'functions' / 'lib' / 'render-article.mjs'
QUALITY = ROOT / 'netlify' / 'functions' / 'lib' / 'learning-quality.mjs'


class DynamicPublishingTests(unittest.TestCase):
    def run_node(self, source):
        return subprocess.run(
            ['node', '--input-type=module', '-e', source],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_renderer_matches_standard_article_sections(self):
        article = {
            'id': 'article_19', 'title': '測試文章', 'category': '管理實踐',
            'reading_minutes': 6, 'subtitle': '副標題', 'summary': '摘要',
            'start_prompt': '開始思考', 'orientation': ['先理解', '再行動'],
            'quick_scan': [], 'case': {'title': '案例', 'scenario': '情境', 'turning_point': '轉折', 'outcome': '結果'},
            'questions': [], 'focus_tips': {}, 'tools': [
                {'label': '工作工具', 'title': '檢核表', 'steps': ['第一步'], 'explanation': '說明'}
            ], 'body_markdown': '## 第一段\n\n正文。\n\n|欄位|內容|\n|---|---|\n|A|B|\n\n## 結語\n\n最後。',
            'hero_image': 'assets/article-19-new.png', 'hero_image_alt': '測試圖',
            'audio_asset': '/api/audio?id=article_19', 'video_url': ''
        }
        source = f"import renderArticle from './{RENDERER.relative_to(ROOT)}'; console.log(renderArticle({json.dumps(article, ensure_ascii=False)}));"
        result = self.run_node(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        html = result.stdout
        for marker in ['class="article-hero-visual"', 'id="s1"', 'id="s2"', 'id="s3"', 'id="s4"', 'id="s5"', 'class="reading-table"', 'class="reading-tool"', 'site-footer']:
            self.assertIn(marker, html)
        self.assertNotIn('工具內容待補充', html)

    def test_empty_tools_are_omitted(self):
        article = {'id': 'article_19', 'title': '測試', 'body_markdown': '正文', 'tools': []}
        source = f"import renderArticle from './{RENDERER.relative_to(ROOT)}'; console.log(renderArticle({json.dumps(article)}));"
        result = self.run_node(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('reading-tool', result.stdout)

    def test_new_publish_ids_start_after_static_articles(self):
        source = (ROOT / 'netlify' / 'functions' / 'api.mjs').read_text()
        self.assertIn('const STATIC_ARTICLE_MAX = 18;', source)
        self.assertIn('let highest = STATIC_ARTICLE_MAX;', source)
        self.assertIn('page: `/article?id=${encodeURIComponent(id)}`', source)

    def test_local_publish_does_not_require_image_generation(self):
        source = (ROOT / 'scripts' / 'author_server.py').read_text()
        publish_block = source[source.index('    def publish_article'):source.index('    def save_published_article')]
        self.assertNotIn('generate-article-image', publish_block)
        self.assertNotIn('主圖生成失敗', publish_block)

    def test_quick_scan_quality_requires_three_complete_questions(self):
        valid = [
            {'question': f'題目 {index}', 'options': [
                {'text': '選項 A', 'feedback': '回饋 A'},
                {'text': '選項 B', 'feedback': '回饋 B'},
            ]}
            for index in range(1, 4)
        ]
        invalid = valid[:2] + [{'question': '缺少選項', 'options': []}]
        source = (
            f"import {{ validateQuickScan }} from './{QUALITY.relative_to(ROOT)}'; "
            f"console.log(JSON.stringify([validateQuickScan({json.dumps(valid, ensure_ascii=False)}), "
            f"validateQuickScan({json.dumps(invalid, ensure_ascii=False)})]));"
        )
        result = self.run_node(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        valid_result, invalid_result = json.loads(result.stdout)
        self.assertTrue(valid_result['valid'])
        self.assertEqual(valid_result['issues'], [])
        self.assertFalse(invalid_result['valid'])
        self.assertIn('第 3 題需要 2 個選項', invalid_result['issues'])

    def test_cloud_and_local_generation_retry_only_quick_scan(self):
        api = (ROOT / 'netlify' / 'functions' / 'api.mjs').read_text()
        local = (ROOT / 'scripts' / 'author_server.py').read_text()
        admin = (ROOT / 'assets' / 'admin.js').read_text()
        self.assertIn("path === '/regenerate-quick-scan'", api)
        self.assertIn("'/api/regenerate-quick-scan'", admin)
        self.assertIn("self.path == '/api/regenerate-quick-scan'", local)
        self.assertIn('validateQuickScan', api)

    def test_workbench_blocks_publish_when_quick_scan_is_incomplete(self):
        admin = (ROOT / 'assets' / 'admin.js').read_text()
        self.assertNotIn('publishArticle', admin)
        self.assertIn('renderQuickScanEditor', admin)

    def test_shared_template_keeps_quick_scan_collapsed_by_default(self):
        renderer = RENDERER.read_text()
        self.assertIn('<details class="quick-scan">', renderer)
        self.assertNotIn('<details class="quick-scan" open>', renderer)

    def test_renderer_recovers_quick_scan_when_cloud_returns_json_string(self):
        article = {
            'id': 'article_19', 'title': '測試', 'body_markdown': '正文',
            'quick_scan': json.dumps([
                {'question': '問題一', 'options': [
                    {'text': '選項一', 'feedback': '回饋一'},
                    {'text': '選項二', 'feedback': '回饋二'},
                ]},
            ], ensure_ascii=False),
        }
        source = f"import renderArticle from './{RENDERER.relative_to(ROOT)}'; console.log(renderArticle({json.dumps(article, ensure_ascii=False)}));"
        result = self.run_node(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('問題一', result.stdout)
        self.assertIn('選項一', result.stdout)

    def test_preview_parses_saved_quick_scan_json_string(self):
        preview = (ROOT / 'assets' / 'preview.js').read_text()
        self.assertIn('JSON.parse(value)', preview)

    def test_workbench_is_draft_only(self):
        template = (ROOT / 'author-admin.template.html').read_text()
        admin = (ROOT / 'assets' / 'admin.js').read_text()
        self.assertNotIn('id="previewArticle"', template)
        self.assertNotIn('id="publishArticle"', template)
        self.assertNotIn("document.getElementById('previewArticle').onclick", admin)
        self.assertNotIn("document.getElementById('publishArticle').onclick", admin)
        self.assertIn('外部影音檔網址（選填）', admin)
        self.assertIn('保存變更', template)


if __name__ == '__main__':
    unittest.main()
