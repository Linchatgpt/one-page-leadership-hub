(async()=>{
  const articleId=window.ARTICLE_DATA?.id;
  if(!articleId)return;

  function syncExternalVideo(url){
    const current=document.querySelector('.external-video');
    const value=String(url||'').trim();
    if(!value){current?.remove();return;}
    let parsed;
    try{parsed=new URL(value);}catch{return;}
    const host=parsed.hostname.replace(/^www\./,'');
    const videoId=host==='youtu.be'?parsed.pathname.slice(1):parsed.searchParams.get('v');
    const aside=document.createElement('aside');
    aside.className='external-video';
    const label=document.createElement('small');
    label.className='kicker';label.textContent='延伸影音';aside.append(label);
    if(videoId&&['youtube.com','m.youtube.com','youtu.be'].includes(host)){
      const frame=document.createElement('div');frame.className='external-video-frame';
      const iframe=document.createElement('iframe');iframe.title='延伸影音播放器';iframe.src='https://www.youtube.com/embed/'+encodeURIComponent(videoId);iframe.loading='lazy';iframe.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';iframe.allowFullscreen=true;
      frame.append(iframe);aside.append(frame);
    }
    const link=document.createElement('a');link.href=parsed.href;link.target='_blank';link.rel='noopener';link.textContent=videoId?'在 YouTube 觀看影片 →':'在新分頁開啟影音 →';aside.append(link);
    if(current)current.replaceWith(aside);else document.querySelector('#s1 .reading-essay')?.append(aside);
  }

  try{
    const response=await fetch('/api/list-published',{cache:'no-store'});
    if(!response.ok)return;
    const article=(await response.json()).find((item)=>item.id===articleId);
    if(article)syncExternalVideo(article.video_url);
  }catch(error){console.warn('latest external video unavailable',error);}
})();
