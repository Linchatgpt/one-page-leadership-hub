(function () {
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  let deferredPrompt = null;

  function addInstallPrompt() {
    if (isStandalone || document.querySelector('.pwa-install')) return;
    const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
    const bar = document.createElement('aside');
    bar.className = 'pwa-install';
    bar.setAttribute('aria-label', '安裝學習中心');
    bar.innerHTML = '<strong>把學習中心放到裝置上</strong><span class="pwa-install-copy">下次可直接回來繼續你的工作練習。</span><button type="button" class="pwa-install-button">' + (isIOS ? '查看加入方式' : '安裝到桌面') + '</button><button type="button" class="pwa-install-close" aria-label="關閉安裝提示">×</button>';
    document.body.appendChild(bar);
    bar.querySelector('.pwa-install-button').addEventListener('click', async function () {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        await deferredPrompt.userChoice;
        deferredPrompt = null;
        bar.remove();
      } else {
        bar.querySelector('.pwa-install-copy').textContent = 'iPhone／iPad：點分享，再選「加入主畫面」。';
      }
    });
    bar.querySelector('.pwa-install-close').addEventListener('click', function () { bar.remove(); });
  }

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredPrompt = event;
    addInstallPrompt();
  });
  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    document.querySelector('.pwa-install')?.remove();
  });
  if (/iphone|ipad|ipod/i.test(navigator.userAgent) && !isStandalone) addInstallPrompt();
  if ('serviceWorker' in navigator) window.addEventListener('load', function () {
    navigator.serviceWorker.register('./service-worker.js').catch(function () {});
  });
})();
