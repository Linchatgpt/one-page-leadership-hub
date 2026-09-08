#!/usr/bin/env python3
import base64, html, json, os, re, ssl, subprocess, tempfile, urllib.request, certifi
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def clean_symbols(value):
    if isinstance(value, str):
        return value.translate(str.maketrans('', '', '*#＊＃'))
    if isinstance(value, list):
        return [clean_symbols(item) for item in value]
    if isinstance(value, dict):
        return {key: clean_symbols(item) for key, item in value.items()}
    return value

def normalize_advanced_result(result):
    title = re.sub(r'\s+', '', str(result.get('title', '')).strip())
    title = re.split(r'[：:，,。！？!?]', title, maxsplit=1)[0].strip() or title
    result['title'] = title[:12]
    body = str(result.get('body_markdown', '')).replace('\r\n', '\n')
    body = re.sub(r'^\s*>\s?', '', body, flags=re.M)
    body = re.sub(r'\n\s*\{[^{}\n]*(?:"title"|"context"|"reflection")[^{}\n]*\}\s*', '\n\n', body, flags=re.S)
    body = re.sub(r'^\s*(?:#{1,6}\s*)?(?:結語|結論|總結)\s*$', '## 總結提要', body, flags=re.M)
    normalized_lines=[]
    for line in body.split('\n'):
        clean=line.strip()
        if (clean and not clean.startswith(('#', '-', '|', '<!--')) and not re.match(r'^\d+[.、）)]', clean)
                and len(clean) <= 28 and not re.search(r'[。！？!?：:；;，,]$', clean)):
            line='## '+clean
        normalized_lines.append(line)
    body='\n'.join(normalized_lines)
    body = re.sub(r'\n{3,}', '\n\n', body).strip()
    result['body_markdown'] = body
    return result

def load_env():
    path = ROOT / '.env'
    if path.is_file():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        path = self.path.split('?', 1)[0]
        if path in ('/author-admin.html', '/preview.html'):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/health':
            self.send_json(200, {'ok': True, 'project': 'one-page-leadership-hub'})
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/generate-article-image':
            self.generate_article_image()
            return
        if self.path == '/api/publish-article':
            self.publish_article()
            return
        if self.path == '/api/generate-audio-script':
            self.generate_audio_script()
            return
        if self.path == '/api/render-preview':
            self.render_preview()
            return
        if self.path == '/api/generate-summary-audio':
            self.generate_summary_audio()
            return
        if self.path == '/api/convert-pdf':
            self.convert_pdf()
            return
        if self.path != '/api/generate-learning-page':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            payload = json.loads(self.rfile.read(length) or '{}')
            source = str(payload.get('source_text', '')).strip()
            if not source:
                raise ValueError('缺少文章正文')
            result = generate(payload)
            self.send_json(200, result)
        except Exception as exc:
            self.log_message('render preview error: %s', exc)
            self.send_json(500, {'error': str(exc)})

    def render_preview(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            article = json.loads(self.rfile.read(length) or '{}')
            article.setdefault('id', 'article_preview')
            article.setdefault('title', '未命名文章')
            article.setdefault('subtitle', '')
            article.setdefault('category', '未分類')
            article.setdefault('reading_minutes', 10)
            article.setdefault('summary', '')
            article.setdefault('meta_description', article['summary'])
            article.setdefault('start_prompt', '讀完這篇文章後，你想帶回哪一個工作情境？')
            article.setdefault('orientation', [])
            article.setdefault('quick_scan', [])
            article.setdefault('case', '')
            article.setdefault('questions', [])
            article.setdefault('tools', [])
            article.setdefault('focus_tips', {})
            for field in ('title', 'subtitle', 'category', 'summary', 'meta_description', 'start_prompt', 'seo_title'):
                if not isinstance(article.get(field), str):
                    article[field] = json.dumps(article.get(field), ensure_ascii=False) if article.get(field) is not None else ''
            article['reading_minutes'] = int(article.get('reading_minutes') or 10)
            article['orientation'] = [str(item) for item in (article.get('orientation') if isinstance(article.get('orientation'), list) else []) if item]
            article['quick_scan'] = [item for item in (article.get('quick_scan') if isinstance(article.get('quick_scan'), list) else []) if isinstance(item, dict) and item.get('question')]
            for item in article['quick_scan']:
                item['options'] = [option for option in item.get('options', []) if isinstance(option, dict) and option.get('text')]
                for option in item['options']: option.setdefault('feedback', '')
            normalized_questions = []
            for item in (article.get('questions') if isinstance(article.get('questions'), list) else []):
                if not isinstance(item, dict) or not item.get('question'): continue
                item.setdefault('label', '學習焦點')
                item['options'] = [str(option) for option in item.get('options', []) if option]
                normalized_questions.append(item)
            article['questions'] = normalized_questions
            normalized_tools = []
            for item in (article.get('tools') if isinstance(article.get('tools'), list) else []):
                if not isinstance(item, dict) or not item.get('title'): continue
                item.setdefault('label', '本篇工作工具')
                item.setdefault('steps', [])
                item.setdefault('explanation', item.get('body', ''))
                normalized_tools.append(item)
            article['tools'] = normalized_tools
            article = normalize_advanced_result(article)
            import sys
            sys.path.insert(0, str(ROOT / 'scripts'))
            from build_article_hub import build_article, SUBSCRIPTION_URL
            html = build_article(article, str(article.get('body_markdown', '')))
            html = html.replace(
                '<a class="subscribe-link" href="'+SUBSCRIPTION_URL+'" target="_blank" rel="noopener">訂閱學習更新</a></div>',
                '<a class="subscribe-link" href="'+SUBSCRIPTION_URL+'" target="_blank" rel="noopener">訂閱學習更新</a><a href="author-admin.html">回到文章工作台</a></div>'
            )
            self.send_response(200)
            raw = html.encode('utf-8')
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except Exception as exc:
            self.log_message('render preview error: %s', exc)
            self.send_json(500, {'error': str(exc)})

    def generate_audio_script(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            payload = json.loads(self.rfile.read(length) or '{}')
            title, body = str(payload.get('title', '')).strip(), str(payload.get('body_markdown', '')).strip()
            if not body: raise ValueError('文章正文為空')
            self.send_json(200, {'audio_script': generate_audio_script(title, body)})
        except Exception as exc:
            self.send_json(500, {'error': str(exc)})

    def publish_article(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            article = json.loads(self.rfile.read(length) or '{}')
            body = str(article.pop('body_markdown', '')).strip()
            if not article.get('title') or not body: raise ValueError('文章標題與正文不可為空')
            image_request = urllib.request.Request(
                f"http://127.0.0.1:{os.environ.get('PORT', '5200')}/api/generate-article-image",
                data=json.dumps(article).encode(), headers={'content-type': 'application/json'})
            with urllib.request.urlopen(image_request, timeout=240) as image_response:
                image_result = json.loads(image_response.read().decode())
            if not image_result.get('hero_image'):
                raise ValueError(image_result.get('error') or '發布前主圖生成失敗')
            article['hero_image'] = image_result['hero_image']
            article['hero_image_alt'] = image_result.get('hero_image_alt') or article.get('title', '')
            article_id = str(article.get('id', ''))
            if not re.fullmatch(r'article_\d+', article_id):
                existing_id = ''
                for path in (ROOT/'content/articles').glob('article_*/article.json'):
                    try:
                        existing = json.loads(path.read_text())
                    except (OSError, json.JSONDecodeError):
                        continue
                    if existing.get('title') == article.get('title'):
                        existing_id = path.parent.name
                        break
                if existing_id:
                    article_id = existing_id
                else:
                    numbers=[int(match.group(1)) for path in (ROOT/'content/articles').glob('article_*/article.json') if (match:=re.match(r'article_(\d+)', path.parent.name))]
                    article_id=f'article_{max(numbers or [0])+1}'
            article['id']=article_id; article['status']='published'
            folder=ROOT/'content/articles'/article_id; folder.mkdir(parents=True, exist_ok=True)
            embedded_audio = article.pop('audio_data', '')
            audio_path = ROOT/'audio_summaries'/f'article_{article_id.split("_")[-1]}_summary.mp3'
            if isinstance(embedded_audio, str) and embedded_audio.startswith('data:audio/mpeg;base64,'):
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                audio_path.write_bytes(base64.b64decode(embedded_audio.split(',', 1)[1]))
                article['audio'] = True
            elif not audio_path.is_file():
                article['audio'] = False
            (folder/'article.json').write_text(json.dumps(article, ensure_ascii=False, indent=2)+'\n')
            (folder/'article.md').write_text(body+'\n')
            subprocess.run(['python3', str(ROOT/'scripts/build_article_hub.py')], cwd=ROOT, check=True, capture_output=True, text=True)
            self.send_json(200, {'ok': True, 'id': article_id, 'page': f'Article_Learning_Article{article_id.split("_")[-1]}.html'})
        except subprocess.CalledProcessError as exc:
            self.send_json(500, {'error': (exc.stderr or exc.stdout or '文章建置失敗').strip()})
        except Exception as exc:
            self.send_json(500, {'error': str(exc)})

    def generate_article_image(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            article = json.loads(self.rfile.read(length) or '{}')
            title = str(article.get('title', '未命名文章')).strip()[:24]
            category = str(article.get('category', '領導學習')).strip()[:24]
            article_id = re.sub(r'[^a-zA-Z0-9_-]+', '-', str(article.get('id', 'draft'))).strip('-') or 'draft'
            key = os.environ.get('AI_API_KEY', '')
            if not key:
                raise ValueError('本機尚未設定 AI_API_KEY，無法生成主圖。')
            variants = ['a small cross-functional group around a table, viewed from a slightly elevated angle', 'a one-to-one coaching conversation with two people in profile, with observers in the background', 'a standing workshop with people arranging cards and diagrams on a wall', 'a quiet reflective scene with one facilitator and several colleagues taking notes', 'a broad team discussion in a bright room, with the main speaker off-center', 'a close conversational moment between two colleagues, with layered group activity behind them']
            seed = sum(ord(char) for char in title) + len(article_id)
            scene_variation = variants[seed % len(variants)]
            prompt = (f'Create a new wide banner editorial illustration for a Traditional Chinese leadership learning website. Subject: {title}. Category: {category}. Scene variation: {scene_variation}. '
                      'The final artwork must be a long horizontal rectangular page-header composition, approximately 2:1, with important people and objects kept inside the central safe area so the image can be displayed as a consistent wide banner without losing the subject. '
                      'Match the established article-15-to-17 visual language: hand-painted watercolor and gouache editorial illustration, warm textured ivory paper, muted olive and deep forest green, ochre gold and restrained terracotta accents, natural expressive people in a real workplace conversation or collaborative learning scene, thoughtful human-centered leadership atmosphere, visible paper grain and soft brush edges, balanced wide landscape composition with layered depth, premium quiet magazine style. '
                      'Keep the same visual identity but deliberately vary the people, age, clothing, camera angle, gestures, room layout, plants, window or mountain elements, and table objects from other articles. Create a new scene specifically for this article. No text, no letters, no numbers, no logos, no watermark, no gradients, no glossy 3D, no photorealism, no generic corporate stock-photo look.')
            endpoint = os.environ.get('AI_IMAGE_API_ENDPOINT', 'https://api.openai.com/v1/images/generations')
            request = urllib.request.Request(endpoint, data=json.dumps({
                'model': os.environ.get('AI_IMAGE_MODEL', 'gpt-image-1'), 'prompt': prompt,
                'size': '1536x1024', 'quality': 'medium', 'output_format': 'png'
            }).encode(), headers={'content-type': 'application/json', 'authorization': f'Bearer {key}'})
            tls_context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(request, timeout=180, context=tls_context) as response:
                data = json.loads(response.read().decode())
            encoded = data.get('data', [{}])[0].get('b64_json')
            if not encoded:
                raise ValueError('圖片服務沒有回傳 PNG。')
            number = re.search(r'(\d+)$', article_id)
            suffix = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:48] or 'leadership-illustration'
            image_name = f"assets/article-{int(number.group(1)):02d}-{suffix}-illustration.png" if number else f'assets/{article_id}-{suffix}-illustration.png'
            image_path = ROOT / image_name
            image_path.write_bytes(base64.b64decode(encoded))
            self.send_json(200, {'hero_image': image_name, 'hero_image_alt': title})
        except Exception as exc:
            self.send_json(500, {'error': str(exc)})

    def convert_pdf(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0:
                raise ValueError('PDF 檔案內容為空')
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(self.rfile.read(length))
                source_path = tmp.name
            try:
                from markitdown import MarkItDown
                result = MarkItDown().convert(source_path)
                markdown = result.text_content.strip()
            finally:
                os.unlink(source_path)
            if not markdown:
                raise ValueError('PDF 沒有可擷取的文字')
            self.send_json(200, {'title': '', 'markdown': clean_symbols(markdown)})
        except ImportError:
            self.send_json(500, {'error': '本機尚未安裝 markitdown'})
        except Exception as exc:
            self.send_json(500, {'error': str(exc)})

    def generate_summary_audio(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            payload = json.loads(self.rfile.read(length) or '{}')
            summary = clean_symbols(str(payload.get('summary', '')).strip())
            summary = re.sub(r'<#[^>]+#>', '', summary)
            summary = re.sub(r'\bModule\s+\d+\s*[,，]?', '', summary, flags=re.I)
            if not summary:
                raise ValueError('摘要內容為空')
            api_key = os.environ.get('MINIMAX_API_KEY', '')
            if not api_key:
                raise RuntimeError('尚未設定 MINIMAX_API_KEY')
            endpoint = os.environ.get('MINIMAX_API_ENDPOINT', 'https://api.minimax.io/v1/t2a_v2')
            payload = {'model': os.environ.get('MINIMAX_MODEL', 'speech-2.8-hd'), 'text': summary, 'stream': False, 'language_boost': 'auto', 'output_format': 'hex', 'voice_setting': {'voice_id': os.environ.get('MINIMAX_VOICE_ID', 'moss_audio_39eb1dad-2537-11f1-9471-ba789c2c93f8'), 'speed': 1.0, 'vol': 1.0, 'pitch': 0}, 'audio_setting': {'sample_rate': 32000, 'bitrate': 128000, 'format': 'mp3', 'channel': 1}}
            request = urllib.request.Request(endpoint, data=json.dumps(payload, ensure_ascii=False).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+api_key}, method='POST')
            with urllib.request.urlopen(request, timeout=120, context=ssl.create_default_context(cafile=__import__('certifi').where())) as response:
                body = json.loads(response.read().decode())
            if body.get('base_resp', {}).get('status_code', 0) != 0: raise RuntimeError(body.get('base_resp', {}).get('status_msg', 'MiniMax 音訊產生失敗'))
            audio = bytes.fromhex(body.get('data', {}).get('audio', ''))
            if not audio: raise RuntimeError('MiniMax 沒有回傳音訊資料')
            self.send_json(200, {'audio_data':'data:audio/mpeg;base64,'+__import__('base64').b64encode(audio).decode()})
        except Exception as exc:
            self.send_json(500, {'error': str(exc)})

    def send_json(self, status, value):
        raw = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format, *args):
        if self.path.startswith('/api/'):
            super().log_message(format, *args)

def generate(payload):
    endpoint = os.environ.get('AI_API_ENDPOINT', 'https://api.openai.com/v1/chat/completions')
    api_key = os.environ.get('AI_API_KEY', '')
    model = os.environ.get('AI_MODEL', 'gpt-5.6-luna')
    effort = os.environ.get('AI_REASONING_EFFORT', 'low')
    if not api_key:
        raise RuntimeError('尚未設定 AI_API_KEY')
    if payload.get('mode') == 'basic':
        system = '''你是繁體中文文字編輯。請整理使用者提供的文章，保留原意、論點、順序與大致篇幅，只修正多餘符號、斷行、標點與 Markdown 標題層級。不要新增學習活動或捏造內容。subtitle 是標題下方的短說明，summary 是首頁文章方格使用的 1 至 2 句短摘要（建議不超過 90 個中文字），不要把整篇文章濃縮成長文。只回傳 JSON，不要 Markdown code fence。欄位必須是：title、subtitle、category、reading_minutes（整數）、summary、body_markdown。'''
    else:
        system = '''你是繁體中文管理學習內容編輯。請把使用者提供的文章整理成可供講師審閱的完整學習型網頁草稿。subtitle 是標題下方的短說明；summary 是首頁文章方格使用的 1 至 2 句短摘要（建議不超過 90 個中文字），不要放入整篇文章內容。tools 必須產生 1 至 2 個文章內可直接使用的工具專欄，每個工具都要有 label、title、steps（3 至 5 個具體步驟）與 explanation，不能回傳空陣列。body_markdown 必須在最相關的正文段落後插入工具位置標記：第一個工具的位置寫成獨立一行 `<!-- TOOL_1 -->`，第二個工具的位置寫成獨立一行 `<!-- TOOL_2 -->`；每個標記最多出現一次，不能把標記放在文章最後集中處，也不要把標記放進 code fence。工具內容仍放在 tools 欄位，不要直接把工具 HTML 寫入正文。只回傳 JSON，不要 Markdown code fence。欄位必須是：title、subtitle、category、reading_minutes（整數）、summary、start_prompt、orientation（4個字串陣列）、quick_scan（3個物件陣列，每個物件有 question、options（2個物件陣列），每個 option 有 text、feedback）、body_markdown、case、questions（4個物件陣列，每個物件有 question、options（2個物件陣列），每個 option 有 text、feedback）、focus_tips（物件，key 對應 questions 選項文字，value 為行動提示）、tools（1 至 2 個物件陣列，每個物件有 label、title、steps（字串陣列）、explanation）。body_markdown 要保留原意並以 Markdown 排版，加入清楚的小標題與段落；互動問題與工作工具要能從文章內容推導，不要捏造事實。'''
    if payload.get('mode') != 'basic':
        system += '''主標題請重新整理為 12 個中文字以內，保留核心意思；完整說明放在 subtitle。body_markdown 必須使用 ## 小標題，表格使用標準 Markdown 表格語法（| 欄位 |），並在文章結尾加入獨立的 ## 總結提要，列出 3 至 5 點短句。工具標記必須放在最相關的正文段落之後，讓正式文章頁能在內文原位置呈現工具方格。不要在正文中加入 HTML、style 或自行設計寬度；情境案例、自我整理與行動欄位必須沿用正式模板的共同欄寬。預覽頁與正式文章頁必須遵守完全相同的文章結構。'''
    user = json.dumps({'title': clean_symbols(payload.get('title','')), 'category': clean_symbols(payload.get('category','')), 'source_text': clean_symbols(payload['source_text'])}, ensure_ascii=False)
    request = urllib.request.Request(endpoint, data=json.dumps({'model': model, 'reasoning_effort': effort, 'messages':[{'role':'system','content':system},{'role':'user','content':user}], 'response_format': {'type':'json_object'}, 'max_completion_tokens':8000}, ensure_ascii=False).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+api_key}, method='POST')
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=120, context=context) as response:
        data = json.loads(response.read())
    content = data['choices'][0]['message']['content']
    result = json.loads(content)
    required = ['title','subtitle','category','reading_minutes','summary','body_markdown'] if payload.get('mode') == 'basic' else ['title','subtitle','category','reading_minutes','summary','start_prompt','orientation','quick_scan','body_markdown','case','questions','focus_tips','tools']
    missing = [key for key in required if key not in result]
    if missing:
        raise RuntimeError('AI 回應缺少欄位：' + ', '.join(missing))
    result = clean_symbols(result)
    return normalize_advanced_result(result) if payload.get('mode') != 'basic' else result

def generate_audio_script(title, body):
    endpoint = os.environ.get('AI_API_ENDPOINT', 'https://api.openai.com/v1/chat/completions')
    api_key = os.environ.get('AI_API_KEY', '')
    if not api_key: raise RuntimeError('尚未設定 AI_API_KEY')
    system = '你是繁體中文音訊編輯。根據文章標題與正文，寫一段約200至220個中文字、適合接在固定開場與結尾之間的口播核心內容，讓整段含固定開場與結尾約250字、約1分鐘。內容要包含核心觀點、關鍵脈絡與一個實務提醒。只回傳口播正文，不要開場、結尾、標題、引號、Module編號、XML標記或時間控制符號。'
    request = urllib.request.Request(endpoint, data=json.dumps({'model':os.environ.get('AI_MODEL','gpt-5.6-luna'),'reasoning_effort':os.environ.get('AI_REASONING_EFFORT','low'),'messages':[{'role':'system','content':system},{'role':'user','content':f'文章標題：{title}\n文章正文：\n{body[:12000]}'}],'max_completion_tokens':300},ensure_ascii=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+api_key},method='POST')
    with urllib.request.urlopen(request, timeout=120, context=ssl.create_default_context(cafile=__import__('certifi').where())) as response:
        data=json.loads(response.read())
    content=str(data['choices'][0]['message']['content']).strip()
    return re.sub(r'<#[^>]+#>|\bModule\s+\d+\s*[,，]?', '', content, flags=re.I).strip('「」"')

if __name__ == '__main__':
    load_env()
    port = int(os.environ.get('PORT', '8765'))
    os.chdir(ROOT)
    print(f'Leadership hub author server: http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
