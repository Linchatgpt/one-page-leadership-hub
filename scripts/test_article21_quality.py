import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Article21QualityTests(unittest.TestCase):
    def test_preview_has_no_markdown_markers_or_audio_delay_tokens(self):
        preview = (ROOT / "preview-article21.html").read_text()
        audio = (ROOT / "audio_summaries/article_21_summary.txt").read_text()
        self.assertNotIn("**", preview)
        self.assertNotIn("<#", audio)
        self.assertNotIn("0050", audio)

    def test_shared_renderer_converts_bold_markdown(self):
        script = """import renderArticle from './netlify/functions/lib/render-article.mjs';
const html = renderArticle({id:'article_21', title:'測試', body_markdown:'**粗體**'});
if (html.includes('**粗體**')) process.exit(1);
if (!html.includes('<strong>粗體</strong>')) process.exit(2);
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
