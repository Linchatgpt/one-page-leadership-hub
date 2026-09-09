(async()=>{
  const esc=(value)=>String(value||'').replace(/[&<>"']/g,(char)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const renderCard=(card,article)=>{
    const number=String(article.number||String(article.id||'').match(/article_(\d+)$/)?.[1]||'').padStart(2,'0');
    const audio=article.audio_data?'<div class="module-audio"><span class="audio-label">播放摘要</span><audio controls preload="none" src="/api/audio?id='+encodeURIComponent(article.id)+'"></audio></div>':'';
    const page=article.page?'/'+String(article.page).replace(/^\/+/, ''):'/article?id='+encodeURIComponent(article.id);
    card.dataset.articleId=article.id;
    card.innerHTML='<a class="map-card-link" href="'+esc(page)+'"><small>ARTICLE '+number+' · '+esc(article.category||'領導學習')+' · '+Number(article.reading_minutes||0)+' MIN READ</small><h3>'+esc(article.title||'未命名文章')+'</h3><p>'+esc(article.summary||'')+'</p><span>開始這篇學習 →</span></a>'+audio;
  };
  try{
    const response=await fetch('/api/list-published',{cache:'no-store'});
    if(!response.ok)return;
    const list=await response.json();
    const groups=[...document.querySelectorAll('.map-group')];
    if(!groups.length)return;
    const cards=[...document.querySelectorAll('.map-card')];
    list.slice().reverse().forEach((article)=>{
      if(!article.id)return;
      const existingCard=document.querySelector('[data-article-id="'+CSS.escape(article.id)+'"]');
      if(existingCard){renderCard(existingCard,article);return;}
      const card=document.createElement('div');
      card.className='map-card';
      renderCard(card,article);
      cards.unshift(card);
    });
    cards.forEach((card,index)=>groups[Math.floor(index/4)]?.appendChild(card));
  }catch(error){console.warn('published articles unavailable',error);}
})();
