/* Co-branding dealer per il configuratore xFarm.
   Il dealer arriva da window.QX_DEALER_SLUG (impostato dalla pagina con password)
   e i suoi dati da window.QX_DEALERS (dentro la parte cifrata).
   Il listino e il configuratore restano quelli ufficiali, uguali per tutti. */
(function () {
  'use strict';
  var css = document.createElement('style');
  css.textContent = '#qxClaudeHowto,#qxPaste{display:none!important}' +
    '.qx-dealer-pill{display:inline-flex;align-items:center;background:#fff;border-radius:8px;padding:4px 10px;height:38px}' +
    '.qx-dealer-pill img{max-height:30px;max-width:170px;display:block}' +
    '.qx-dealer-x{color:#fff;opacity:.85;font-size:18px;margin:0 8px 0 10px}';
  document.head.appendChild(css);

  var slug = String(window.QX_DEALER_SLUG || '');
  var D = (window.QX_DEALERS || {})[slug];
  if (!D) return; // senza dealer: configuratore xFarm normale

  // link generico (/xfarm/): solo logo xFarm, nessun logo dealer
  var logoUrl = (!D.generico && D.logo) ? D.logo : '';

  function addBrand() {
    if (D.generico) return;
    var xf = document.querySelector('.topbar .brand-logo');
    if (!xf || document.querySelector('.qx-dealer-pill')) return;
    var x = document.createElement('span'); x.className = 'qx-dealer-x'; x.textContent = '×';
    var pill = document.createElement('span'); pill.className = 'qx-dealer-pill';
    if (logoUrl) { var im = document.createElement('img'); im.src = logoUrl; im.alt = D.name; pill.appendChild(im); }
    else { pill.textContent = D.name; pill.style.fontWeight = '700'; }
    xf.insertAdjacentElement('afterend', x); x.insertAdjacentElement('afterend', pill);
    document.title = D.name + ' × xFarm — Configuratore preventivi';
  }

  /* logo "xFarm × dealer" nell'intestazione di PDF e Word */
  var pdfLogoReady = null;
  function loadImg(src) {
    return new Promise(function (res) { var i = new Image(); i.onload = function () { res(i); }; i.onerror = function () { res(null); }; i.src = src; });
  }
  function buildPdfLogo() {
    if (pdfLogoReady) return pdfLogoReady;
    pdfLogoReady = (async function () {
      if (typeof QX_LOGO_B64 === 'undefined' || !logoUrl) return;
      var xf = await loadImg(QX_LOGO_B64), dl = await loadImg(logoUrl);
      if (!xf || !dl) return;
      var H = xf.naturalHeight || 143, pad = Math.round(H * 0.12), gap = Math.round(H * 0.45);
      var innerH = H - 2 * pad, dlW = dl.naturalWidth || 420, dlH = dl.naturalHeight || 120;
      var dw = Math.min(Math.round(dlW * innerH / dlH), Math.round(H * 3.2));
      var dh = Math.min(innerH, Math.round(dlH * dw / dlW));
      var pillW = dw + 2 * pad, W = xf.naturalWidth + gap + pillW;
      var c = document.createElement('canvas'); c.width = W; c.height = H;
      var g = c.getContext('2d');
      g.drawImage(xf, 0, 0);
      g.fillStyle = 'rgba(255,255,255,.9)'; g.font = Math.round(H * 0.42) + 'px sans-serif';
      g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('×', xf.naturalWidth + gap / 2, H / 2);
      var x0 = xf.naturalWidth + gap, r = Math.round(H * 0.14);
      g.fillStyle = '#ffffff'; g.beginPath();
      g.moveTo(x0 + r, 0); g.lineTo(x0 + pillW - r, 0); g.quadraticCurveTo(x0 + pillW, 0, x0 + pillW, r);
      g.lineTo(x0 + pillW, H - r); g.quadraticCurveTo(x0 + pillW, H, x0 + pillW - r, H);
      g.lineTo(x0 + r, H); g.quadraticCurveTo(x0, H, x0, H - r); g.lineTo(x0, r); g.quadraticCurveTo(x0, 0, x0 + r, 0); g.fill();
      g.drawImage(dl, x0 + pad, Math.round((H - dh) / 2), dw, dh);
      try { QX_LOGO_B64 = c.toDataURL('image/png'); } catch (e) {}
    })();
    return pdfLogoReady;
  }
  ['qxPdf', 'qxWord', 'qxPdfArtifact', 'qxWordArtifact'].forEach(function (fn) {
    var orig = window[fn];
    if (typeof orig !== 'function') return;
    window[fn] = async function () { await buildPdfLogo(); return orig.apply(this, arguments); };
  });

  function start() {
    addBrand();
    var ls = document.getElementById('langSelect'), done = false;
    try { done = !!sessionStorage.getItem('qxDealerLang'); } catch (e) {}
    if (ls && D.lang && ls.value !== D.lang && !done) {
      try { sessionStorage.setItem('qxDealerLang', '1'); } catch (e) {}
      ls.value = D.lang; ls.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
  window.addEventListener('load', function () { addBrand(); buildPdfLogo(); });
})();
