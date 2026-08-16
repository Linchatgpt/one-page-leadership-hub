#!/usr/bin/env python3
"""Build Article Hub learner pages and the generated root map."""
from pathlib import Path
import html, json, re

ROOT=Path(__file__).resolve().parents[1]; ARTICLES=ROOT/'content/articles'; TEMPLATE=ROOT/'templates/article_learning_template.html'
SITE_URL='https://leading4elite.com/'
SUBSCRIPTION_URL='https://script.google.com/macros/s/AKfycbzYRJwtPdcxHQvdcskw1culJfrb6q2-JqJ6F__To56XfvMw8VHDJEv6quyVmMAS8EIu/exec?source=%E7%B2%BE%E8%90%83%E9%A0%98%E5%B0%8E%E2%84%A2%E5%AD%B8%E7%BF%92%E4%B8%AD%E5%BF%83'
PWA_HEAD='<link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#17352e"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="精萃領導"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png">'
PWA_SCRIPT='<script src="pwa.js" defer></script>'

def inject_pwa(document):
    if 'rel="manifest"' in document and 'src="pwa.js"' in document:
        return document
    return document.replace('</head>', PWA_HEAD+'</head>').replace('</body>', PWA_SCRIPT+'</body>')

def md_to_html(text):
    out=[]; para=[]; in_ul=False; summary_open=False; seen_h1=False
    def flush():
        nonlocal para
        if para: out.append('<p>'+ '<br>'.join(para) +'</p>'); para=[]
    for raw in text.splitlines():
        line=raw.strip()
        if line == '<!-- TOOL_1 -->':
            flush(); out.append('__TOOL_1__'); continue
        if line == '<!-- TOOL_2 -->':
            flush(); out.append('__TOOL_2__'); continue
        if line == '<!-- TOOL_3 -->':
            flush(); out.append('__TOOL_3__'); continue
        if not line: flush(); continue
        if line.startswith('### '):
            flush()
            out.append('<h3>'+html.escape(line[4:])+'</h3>')
            continue
        if line.startswith('# '):
            flush()
            if not seen_h1: seen_h1=True
            else: out.append('<h1>'+html.escape(line[2:])+'</h1>')
            continue
        if line.startswith('## '):
            flush()
            heading=line[3:]
            if heading=='總結提要':
                out.append('<div class="reading-summary"><span class="summary-label">深入閱讀收束</span><h2>總結提要</h2>'); summary_open=True
            else: out.append('<h2>'+html.escape(heading)+'</h2>')
            continue
        if line.startswith('- '):
            if not in_ul: flush(); out.append('<ul>'); in_ul=True
            out.append('<li>'+html.escape(line[2:])+'</li>'); continue
        if in_ul: out.append('</ul>'); in_ul=False
        para.append(html.escape(line))
    flush()
    if in_ul: out.append('</ul>')
    if summary_open: out.append('</div>')
    return '\n'.join(out).replace('導言｜','<strong>導言｜</strong>')

def scan_html(items):
    blocks=[]
    for i,item in enumerate(items):
        opts=''.join(f'<button type="button" data-feedback="{html.escape(o["feedback"], quote=True)}">{html.escape(o["text"])}</button>' for o in item['options'])
        blocks.append(f'<div class="scan-question"><p>{i+1:02d} · {html.escape(item["question"])}</p><div class="scan-options">{opts}</div><p class="scan-feedback" aria-live="polite"></p></div>')
    return ''.join(blocks)

def questions_html(items):
    blocks=[]
    for i,item in enumerate(items):
        if isinstance(item, dict): label,q,options=item['label'],item['question'],item['options']
        else:
            label,q=item; options=["先記下這個線索","先試一個小改變"]
        buttons=''.join(f'<label class="assessment-option"><input type="radio" name="q{i}" value="{html.escape(label)}" data-option="{html.escape(text)}" data-key="q{i}"><span>{html.escape(text)}</span></label>' for text in options)
        blocks.append(f'<fieldset class="question"><legend><span class="question-number">{i+1}.</span> {html.escape(q)}</legend><div class="assessment-options">{buttons}</div><small class="question-label">{html.escape(label)}</small></fieldset>')
    return ''.join(blocks)

def tools_html(items):
    extension='使用時可先在一個真實工作情境中填寫，完成後再回看結果與影響；如果發現記錄仍然太抽象，就補上一個具體事件、對話或下一步，讓這張工具卡不只幫助思考，也能留下下次回饋與修正的依據。'
    cards=[]
    for x in items:
        if x.get('steps') and x.get('explanation'):
            steps='<br>'.join(html.escape(step) for step in x['steps'])
            body=f'<p class="tool-steps"><strong>{steps}</strong></p><p>{html.escape(x["explanation"] + extension)}</p>'
        else:
            body=f'<p>{html.escape(x["body"] + extension)}</p>'
        cards.append(f'<aside class="reading-tool"><span class="tool-label">{html.escape(x["label"])}</span><h3>{html.escape(x["title"])}</h3>{body}</aside>')
    return ''.join(cards)

def audio_card_html(number, enabled=True):
    if not enabled: return ''
    src=f'audio_summaries/article_{number}_summary.mp3'
    return f'<div class="module-audio"><span class="audio-label">播放摘要</span><audio controls preload="none" aria-label="播放文章 {number} 摘要" src="{src}"></audio></div>'

def build_article(d, md):
    t=TEMPLATE.read_text(); tools=tools_html(d.get('tools',[])); tool_parts=tools.split('</aside>')
    has_inline_tools='<!-- TOOL_1 -->' in md or '<!-- TOOL_2 -->' in md or '<!-- TOOL_3 -->' in md
    article_html=md_to_html(md).replace('__TOOL_1__', tool_parts[0]+'</aside>')
    for marker,index in [('__TOOL_2__',1),('__TOOL_3__',2)]:
        if marker in article_html and index < len(tool_parts):
            article_html=article_html.replace(marker, tool_parts[index]+'</aside>')
    image=d.get('hero_image','')
    image_html=f'<figure class="article-hero-visual"><img src="{html.escape(image)}" alt="{html.escape(d.get("hero_image_alt","文章主題插圖"))}"></figure>' if image else ''
    number=d['id'].split('_')[-1]; page=f'Article_Learning_Article{number}.html'; canonical=SITE_URL+page
    image_url=SITE_URL+image if image else ''
    schema={'@context':'https://schema.org','@type':'Article','headline':d.get('seo_title',d['title']),'description':d.get('meta_description',d['summary']),'inLanguage':'zh-Hant-TW','mainEntityOfPage':{'@type':'WebPage','@id':canonical},'author':{'@type':'Person','name':d.get('author_name','林祖威教練'),'url':d.get('author_url','https://leading4elite.com/about_wesley/')},'publisher':{'@type':'Organization','name':'精萃領導™學習中心'},'image':image_url}
    replacements={'TITLE':d['title'],'SEO_TITLE':d.get('seo_title',d['title']+'｜精萃領導™學習中心'),'META_DESCRIPTION':d.get('meta_description',d['summary']),'CANONICAL_URL':canonical,'OG_IMAGE':image_url,'ARTICLE_SCHEMA':html.escape(json.dumps(schema,ensure_ascii=False),quote=False),'SUBTITLE':d.get('subtitle','把觀點帶回一個可觀察的工作行動'),'PROJECT_TITLE':'精萃領導™學習中心','NUMBER':number,'CATEGORY':d['category'],'READING_MINUTES':str(d['reading_minutes']),'SUMMARY':d['summary'],'START_PROMPT':d['start_prompt'],'ORIENTATION':''.join('<li>'+html.escape(x)+'</li>' for x in d['orientation']),'QUICK_SCAN':scan_html(d['quick_scan']),'ARTICLE_HTML':article_html,'TOOLS':'' if has_inline_tools else tools,'ARTICLE_IMAGE':image_html,'CASE':d['case'],'QUESTIONS':questions_html(d['questions']),'ARTICLE_DATA':json.dumps(d,ensure_ascii=False)}
    t=t.replace('<section id="s1">','{{ARTICLE_IMAGE}}<section id="s1">')
    for k,v in replacements.items(): t=t.replace('{{'+k+'}}',v)
    t=t.replace('href="assets/article-learning.css"','href="assets/article-learning.css?v=20260814pwa1"')
    t=t.replace('1:1','1 on 1').replace('1：1','1 on 1')
    t=t.replace('先讀懂，再帶回現場','實用概念').replace('把觀點帶回工作現場','帶回現場').replace('整理一個可觀察的焦點','整理焦點').replace('把觀察留下來','留下觀察').replace('只承諾一個小型試做','我的實踐')
    t=t.replace('<div class="assess">','<details class="self-review"><summary><span><small>SELF REVIEW</small><strong>自我整理（4題）</strong></span><b>點擊展開／收起</b></summary><div class="self-review-body"><div class="assess">').replace('<p id="assessmentMessage" class="assessment-message" aria-live="polite"></p><div id="assessmentResult" class="result"></div></section>','<p id="assessmentMessage" class="assessment-message" aria-live="polite"></p><div id="assessmentResult" class="result"></div></div></details></section>')
    return t

def build_whitepaper(d, md):
    number=d['id'].split('_')[-1]; page=f'Article_Learning_Article{number}.html'; canonical=SITE_URL+page
    schema={'@context':'https://schema.org','@type':'Article','headline':d.get('seo_title',d['title']),'description':d.get('meta_description',d['summary']),'inLanguage':'zh-Hant-TW','mainEntityOfPage':{'@type':'WebPage','@id':canonical},'author':{'@type':'Person','name':d.get('author_name','林祖威教練'),'url':d.get('author_url','https://leading4elite.com/about_wesley/')},'publisher':{'@type':'Organization','name':'精萃領導™學習中心'}}
    pages=''.join(f'<figure class="whitepaper-page"><img src="{html.escape(x["image"])}" alt="{html.escape(x["alt"])}"></figure>' for x in d.get('pages',[]))
    # The rendered PDF pages already contain the original text and illustrations;
    # do not duplicate the full extracted copy beside them in the visual whitepaper.
    body=''
    return inject_pwa(f'''<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(d.get('seo_title',d['title']))}</title><meta name="description" content="{html.escape(d['meta_description'])}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(d.get('seo_title',d['title']))}"><meta property="og:description" content="{html.escape(d['meta_description'])}"><script type="application/ld+json">{html.escape(json.dumps(schema,ensure_ascii=False),quote=False)}</script><link rel="stylesheet" href="assets/article-learning.css?v=20260814pwa1"></head><body><div class="top article-top"><a class="brand" href="index.html" aria-label="返回精萃領導TM學習中心"><i>LE</i> 精萃領導™學習中心</a><span class="save">WHITEPAPER</span></div><div class="whitepaper-layout"><aside class="whitepaper-side"><small>ARTICLE {number} · WHITEPAPER</small><h2>{html.escape(d['title'])}</h2><p>{html.escape(d.get('source_date',''))}</p><a class="whitepaper-download" href="{html.escape(d['pdf_download'])}" download>下載原始 PDF</a></aside><main class="whitepaper-main"><header class="whitepaper-hero"><small class="kicker">{html.escape(d['category'])}</small><h1>{html.escape(d['title'])}</h1><h2>{html.escape(d['subtitle'])}</h2><p class="lead">{html.escape(d['summary'])}</p><p class="whitepaper-note">{html.escape(d.get('source_note',''))}</p><p class="whitepaper-author">{html.escape(d.get('source_date',''))} · By {html.escape(d.get('author_name','林祖威教練'))}</p></header><section class="whitepaper-reading"><div class="reading-essay">{body}</div>{pages}</section><footer class="site-footer article-footer"><div><strong>精萃領導™學習中心</strong><a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a><a href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com" target="_blank" rel="noopener">wesley.lin@leading4elite.com</a><a class="subscribe-link" href="{SUBSCRIPTION_URL}" target="_blank" rel="noopener">訂閱學習更新</a></div><img src="assets/line-qr.png" alt="加入 LINE 諮詢領眾課程"></footer></main></div></body></html>''')

def main():
    missing=[]
    for folder in sorted(ARTICLES.iterdir()):
        if not folder.is_dir(): continue
        d=json.loads((folder/'article.json').read_text())
        image=d.get('hero_image','')
        if image and not (ROOT/image).is_file(): missing.append(f'{d.get("id", folder.name)}: {image}')
        number=d.get('id', folder.name).split('_')[-1]
        audio=ROOT/'audio_summaries'/f'article_{number}_summary.mp3'
        if d.get('audio', True) and not audio.is_file(): missing.append(f'{d.get("id", folder.name)}: {audio.relative_to(ROOT)}')
    if missing:
        raise FileNotFoundError('Missing hero image asset(s): ' + '; '.join(missing))
    article_folders=[folder for folder in sorted(ARTICLES.iterdir(), reverse=True) if folder.is_dir()]
    card_groups=[]
    for start in range(0,len(article_folders),4):
        group_cards=[]
        for folder in article_folders[start:start+4]:
            d=json.loads((folder/'article.json').read_text()); page=f'Article_Learning_{d["id"].replace("article_", "Article")}.html'; article_html=(build_whitepaper(d,(folder/'article.md').read_text()) if d.get('layout')=='whitepaper' else build_article(d,(folder/'article.md').read_text())).replace('<div class="top">','<div class="top article-top">').replace('<footer class="site-footer">','<footer class="site-footer article-footer">').replace('<a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a></div>','<a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a><a href="mailto:wesley.lin@leading4elite.com">wesley.lin@leading4elite.com</a></div>'); article_html=article_html.replace('mailto:wesley.lin@leading4elite.com','https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com').replace('href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com">','href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com" target="_blank" rel="noopener">'); (ROOT/page).write_text(article_html)
            if 'class="subscribe-link"' not in article_html:
                article_html=article_html.replace('</div><img src="assets/line-qr.png"', '<a class="subscribe-link" href="'+SUBSCRIPTION_URL+'" target="_blank" rel="noopener">訂閱學習更新</a></div><img src="assets/line-qr.png"')
            (ROOT/page).write_text(inject_pwa(article_html))
            number=d["id"].split("_")[-1]
            search_terms=[d.get('title',''),d.get('subtitle',''),d.get('category',''),d.get('summary',''),d.get('primary_keyword',''),*d.get('related_keywords',[]),*d.get('likely_search_questions',[])]
            search_text=html.escape(' '.join(str(term) for term in search_terms if term), quote=True)
            group_cards.append(f'<div class="map-card" data-search="{search_text}"><a class="map-card-link" href="{page}"><small>ARTICLE {number} · {html.escape(d["category"])} · {d["reading_minutes"]} MIN READ</small><h3>{html.escape(d["title"])}</h3><p>{html.escape(d["summary"])}</p><span>開始這篇學習 →</span></a>{audio_card_html(number,d.get("audio",True))}</div>')
        card_groups.append('<div class="map-group'+(' is-active' if start==0 else '')+'" data-group="'+str(start//4)+'">'+''.join(group_cards)+'</div>')
    cards=''.join(card_groups)
    for folder in []:
        if not folder.is_dir(): continue
        d=json.loads((folder/'article.json').read_text()); page=f'Article_Learning_{d["id"].replace("article_", "Article")}.html'; article_html=build_article(d,(folder/'article.md').read_text()).replace('<div class="top">','<div class="top article-top">').replace('<footer class="site-footer">','<footer class="site-footer article-footer">').replace('<a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a></div>','<a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a><a href="mailto:wesley.lin@leading4elite.com">wesley.lin@leading4elite.com</a></div>'); article_html=article_html.replace('mailto:wesley.lin@leading4elite.com','https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com').replace('href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com">','href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com" target="_blank" rel="noopener">'); (ROOT/page).write_text(article_html)
        article_html=article_html.replace('</div><img src="assets/line-qr.png"', '<a class="subscribe-link" href="'+SUBSCRIPTION_URL+'" target="_blank" rel="noopener">訂閱學習更新</a></div><img src="assets/line-qr.png"')
        (ROOT/page).write_text(inject_pwa(article_html))
        number=d["id"].split("_")[-1]
        cards.append(f'<div class="map-card"><a class="map-card-link" href="{page}"><small>ARTICLE {number} · {html.escape(d["category"])} · {d["reading_minutes"]} MIN READ</small><h3>{html.escape(d["title"])}</h3><p>{html.escape(d["summary"])}</p><span>開始這篇學習 →</span></a>{audio_card_html(number)}</div>')
    index='''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>精萃領導™學習中心</title><link rel="stylesheet" href="assets/article-learning.css"><style>.home-top{{max-width:1400px;margin:auto;padding-left:5vw;padding-right:5vw}}.home-shell{{max-width:1400px;margin:auto;padding:52px 5vw 90px;display:grid;grid-template-columns:250px minmax(0,920px);gap:70px;align-items:start}}.coach-panel{{position:sticky;top:104px;border-top:3px solid var(--gold);padding:22px 0;color:var(--muted)}}.coach-panel h2{{font:24px/1.35 Georgia;color:var(--ink);margin:10px 0 16px}}.coach-panel p{{font-size:13px;line-height:1.9;margin:0 0 14px}}.coach-panel a{{display:inline-block;color:var(--sage);font-weight:700;text-decoration:none;border-bottom:1px solid var(--sage)}}.coach-panel .coach-role{{font-size:11px;letter-spacing:.08em;color:var(--gold)}}.home{{padding:0;max-width:none}}.home-hero{{max-width:920px;padding:20px 0 70px}}.home-hero h1{{font:clamp(40px,6vw,72px)/1.05 Georgia;margin:20px 0;white-space:nowrap}}.home-hero em{{color:var(--sage);font-style:normal}}.home-hero p{{font:20px/1.9 Georgia;color:#456057;max-width:700px}}.home-hero .storage-note{{display:block;font:13px/1.6 "Noto Sans TC",system-ui,sans-serif;color:var(--muted);margin-top:12px}}.map-tools{{display:flex;gap:12px;align-items:center;margin:18px 0 14px}}.map-search{{flex:1;min-height:44px;box-sizing:border-box;padding:10px 14px;border:1px solid var(--line);background:#fff;color:var(--ink);font:inherit}}.map-search:focus{{outline:2px solid var(--gold);outline-offset:2px}}.map-search::placeholder{{color:var(--muted)}}.clear-search{{min-height:44px;padding:10px 15px;border:1px solid var(--line);background:var(--paper);color:var(--ink);font:inherit;cursor:pointer}}.clear-search:hover,.clear-search:focus-visible{{border-color:var(--gold);color:var(--gold)}}.map-controls{{display:flex;align-items:center;justify-content:space-between;margin:16px 0 14px}}.map-controls button{{min-height:44px;padding:10px 16px;border:1px solid var(--line);background:var(--paper);color:var(--ink);font:inherit;cursor:pointer}}.map-controls button:hover,.map-controls button:focus-visible{{border-color:var(--gold);color:var(--gold)}}.map-controls button:disabled{{opacity:.35;cursor:not-allowed}}.map-page{{font-size:12px;color:var(--muted);letter-spacing:.08em}}.map{{display:block}}.map-group{{display:none;grid-template-columns:repeat(2,1fr);gap:16px}}.map-group.is-active{{display:grid}}.map-card{{display:block;color:var(--ink);padding:28px;background:#fff;border:1px solid var(--line);transition:transform .2s,border-color .2s}}.map-card.is-hidden{{display:none}}.map-card:hover{{transform:translateY(-3px);border-color:var(--gold)}}.map-card-link{{display:block;color:var(--ink);text-decoration:none}}.map-card-link:hover,.map-card-link:focus-visible{{color:var(--ink)}}.map-card h3{{font:clamp(21px,2.2vw,28px)/1.2 Georgia;margin:12px 0 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.map-card p{{color:var(--muted);font-size:14px}}.module-audio{{display:flex;align-items:center;gap:10px;margin-top:18px;padding-top:14px;border-top:1px solid var(--line)}}.audio-label{{color:var(--muted);font-size:12px;white-space:nowrap}}.module-audio audio{{display:block;width:100%;max-width:270px;height:32px}}.search-empty{{display:none;padding:28px;border:1px dashed var(--line);color:var(--muted)}}.search-empty.is-visible{{display:block}}.home-footer{{max-width:1400px;margin:60px auto 0;padding-left:calc(5vw + 320px);padding-right:5vw}}@media(max-width:700px){{.map-tools{{align-items:stretch}}.clear-search{{padding-left:12px;padding-right:12px}}.map{{grid-template-columns:1fr}}.home-hero h1{{white-space:normal;font-size:clamp(40px,11vw,58px)}}.module-audio{{align-items:flex-start;flex-wrap:wrap}.module-audio audio{{max-width:none;flex:1 1 220px}}}}@media(max-width:900px){{.home-shell{{grid-template-columns:1fr;gap:18px;padding-top:28px}}.coach-panel{{display:none}}.home{{order:1}}.home-footer{{padding-left:5vw}}}}</style></head><body><div class="top home-top"><a class="brand" href="index.html" aria-label="返回精萃領導TM學習中心"><i>LE</i> 精萃領導™學習中心</a><span class="save">LOCAL LEARNING HUB</span></div><div class="home-shell"><aside class="coach-panel"><small class="coach-role">LEADERSHIP COACH · FOUNDER</small><h2>林祖威（Wesley）教練</h2><p>領導力教練與講師，擁有十年以上教練經歷，專注於教練型領導力、組織發展與企業教練文化。</p><p>他曾任高科技公司主管、企業主管教練與團隊學習教練，致力協助管理者提升執行力、當責與帶動團隊成長的能力。</p><a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">了解更多教練介紹 →</a></aside><main class="home"><section class="home-hero"><small class="kicker">ONE PAGE · ONE PRACTICE</small><h1>把一篇文章，<em>讀成一個行動。</em></h1><p>每次只帶一個真實工作情境進來：先讀懂，再辨識，再試做。<span class="storage-note">說明：所有學習紀錄只留在你目前瀏覽器所在，不保存網上副本）</span></p></section><section><small class="kicker">LEARNING MAP</small><h2>選一篇，開始你的工作練習。</h2><div class="map-tools"><label class="sr-only" for="articleSearch">搜尋文章主題</label><input id="articleSearch" class="map-search" type="search" placeholder="搜尋文章主題，例如：教練、當責、正念" autocomplete="off"><button type="button" class="clear-search" id="clearSearch">清除</button></div><div class="map-controls"><button type="button" id="newerArticles" disabled>較新文章</button><span class="map-page" id="mapPage" aria-live="polite"></span><button type="button" id="olderArticles">較舊文章</button></div><div class="map"><div class="search-empty" id="searchEmpty">找不到相關文章，請換個主題或關鍵字。</div>__CARDS__</div></section></main></div><footer class="site-footer home-footer"><div><strong>精萃領導™學習中心</strong><a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a></div><img src="assets/line-qr.png" alt="加入 LINE 諮詢領眾課程"></footer>__AUDIO_SCRIPT__</body></html>'''
    index=index.replace('href="assets/article-learning.css"><style>','href="assets/article-learning.css?v=20260814pwa1"><style>').replace('.map{{grid-template-columns:1fr}}','.map{{grid-template-columns:1fr}}.map-group{{grid-template-columns:1fr}}.map-group.is-active{{display:block}}').replace('{{','{').replace('}}','}').replace('__CARDS__', cards).replace('__AUDIO_SCRIPT__', '<script>const articleGroups=[...document.querySelectorAll(".map-group")];const articleCards=[...document.querySelectorAll(".map-card")];let articleGroupIndex=0;const newerArticles=document.getElementById("newerArticles"),olderArticles=document.getElementById("olderArticles"),mapPage=document.getElementById("mapPage"),articleSearch=document.getElementById("articleSearch"),clearSearch=document.getElementById("clearSearch"),searchEmpty=document.getElementById("searchEmpty");function updateArticleGroup(){articleGroups.forEach((group,index)=>group.classList.toggle("is-active",index===articleGroupIndex));newerArticles.disabled=articleGroupIndex===0;olderArticles.disabled=articleGroupIndex===articleGroups.length-1;mapPage.textContent=`${articleGroupIndex+1} / ${articleGroups.length}`;}function filterArticles(){const query=articleSearch.value.trim().toLocaleLowerCase();let matches=0;articleCards.forEach(card=>{const match=!query||card.dataset.search.toLocaleLowerCase().includes(query);card.classList.toggle("is-hidden",!match);if(match)matches++;});if(query){articleGroups.forEach(group=>group.classList.add("is-active"));newerArticles.hidden=true;olderArticles.hidden=true;mapPage.textContent=`找到 ${matches} 篇`; }else{newerArticles.hidden=false;olderArticles.hidden=false;updateArticleGroup();}searchEmpty.classList.toggle("is-visible",Boolean(query)&&matches===0);}newerArticles.addEventListener("click",()=>{if(articleGroupIndex>0){articleGroupIndex--;updateArticleGroup();}});olderArticles.addEventListener("click",()=>{if(articleGroupIndex<articleGroups.length-1){articleGroupIndex++;updateArticleGroup();}});articleSearch.addEventListener("input",filterArticles);clearSearch.addEventListener("click",()=>{articleSearch.value="";articleSearch.focus();filterArticles();});updateArticleGroup();document.querySelectorAll(".module-audio audio").forEach((audio)=>{audio.addEventListener("play",()=>{document.querySelectorAll(".module-audio audio").forEach((other)=>{if(other!==audio)other.pause();});});});</script>').replace('1:1','1 on 1').replace('1：1','1 on 1')
    index=index.replace('<a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a></div>','<a href="https://leading4elite.com/about_wesley/" target="_blank" rel="noopener">林祖威教練</a><a href="mailto:wesley.lin@leading4elite.com">wesley.lin@leading4elite.com</a></div>')
    index=index.replace('mailto:wesley.lin@leading4elite.com','https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com').replace('href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com">','href="https://mail.google.com/mail/?view=cm&amp;fs=1&amp;to=wesley.lin%40leading4elite.com" target="_blank" rel="noopener">').replace('不保存網上副本）','不保存網上副本')
    index=index.replace('</div><img src="assets/line-qr.png"', '<a class="subscribe-link" href="'+SUBSCRIPTION_URL+'" target="_blank" rel="noopener">訂閱學習更新</a></div><img src="assets/line-qr.png"')
    (ROOT/'index.html').write_text(inject_pwa(index))
if __name__=='__main__': main()
