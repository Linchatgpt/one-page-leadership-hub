import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / 'netlify' / 'functions' / 'lib' / 'render-article.mjs'


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


if __name__ == '__main__':
    unittest.main()
