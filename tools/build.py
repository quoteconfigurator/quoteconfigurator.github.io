#!/usr/bin/env python3
"""Rigenera il sito dei dealer con il configuratore cifrato.

Uso:
  python3 tools/build.py <cartella sorgente>   # nuovo configuratore (index.html + assets/)
  python3 tools/build.py                       # stesso configuratore: dealer o password cambiati

Richiede: pip install cryptography

Cosa fa:
- cifra il configuratore (con dentro i dati dei dealer: nome, logo, lingua) in app/app.enc
  con AES-256-GCM e una chiave casuale nuova a ogni build;
- per ogni dealer di dealers.json crea <dealer>/index.html: una pagina che chiede la password
  e contiene la chiave del configuratore cifrata con quella password (PBKDF2-SHA256, 600.000 iterazioni);
- le password NON stanno nel repository: le chiede a ogni build (oppure le legge da
  passwords.local.json, un file solo sul tuo computer, escluso da git);
- elimina le cartelle dei dealer tolti da dealers.json;
- rigenera la tabella dei link in README.md.

Senza cartella sorgente il configuratore attuale viene recuperato decifrando app/app.enc
con una delle password inserite.
"""
import base64, hashlib, html, json, mimetypes, os, re, secrets, shutil, sys

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    sys.exit('Manca la libreria "cryptography": esegui  pip install cryptography  e riprova.')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
ITERATIONS = 600_000
BUILD_START, BUILD_END = '<!--QX-BUILD-->', '<!--/QX-BUILD-->'
TABLE_START, TABLE_END = '<!-- DEALERS:START -->', '<!-- DEALERS:END -->'
LOCAL_PASSWORDS = 'passwords.local.json'  # escluso da git (.gitignore)


def path(*p):
    return os.path.join(ROOT, *p)


def read_json(name, default=None):
    if default is not None and not os.path.exists(path(name)):
        return default
    with open(path(name), encoding='utf-8') as f:
        return json.load(f)


def write_json(name, data):
    with open(path(name), 'w', encoding='utf-8') as f:
        f.write('{\n' + ',\n'.join(f' {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}'
                                   for k, v in data.items()) + '\n}\n')


def b64(b):
    return base64.b64encode(b).decode()


def kek(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS, 32)


def ask_passwords(dealers):
    """Password da passwords.local.json se c'è, altrimenti chieste a terminale."""
    saved = read_json(LOCAL_PASSWORDS, {})
    out = {}
    for slug, d in dealers.items():
        pw = (saved.get(slug) or '').strip()
        while not pw:
            pw = input(f'Password per {d["name"]} ({slug}): ').strip()
        out[slug] = pw
    return out


def page_config(slug):
    """Legge la configurazione (sale, chiave cifrata) da una pagina dealer già generata."""
    p = path(slug, 'index.html')
    if not os.path.exists(p):
        return None
    m = re.search(r'<script id="qx-cfg" type="application/json">(.*?)</script>',
                  open(p, encoding='utf-8').read(), re.S)
    return json.loads(m.group(1)) if m else None


def recover_source(passwords):
    """Decifra app/app.enc con la password di un dealer e toglie le aggiunte della build precedente."""
    enc = path('app', 'app.enc')
    if not os.path.exists(enc):
        sys.exit('Non trovo app/app.enc: indica la cartella del configuratore, es. python3 tools/build.py engine-src')
    blob = open(enc, 'rb').read()
    pages = [c for c in (page_config(n) for n in sorted(os.listdir(ROOT))) if c]
    candidates = list(dict.fromkeys(passwords.values()))
    while True:
        for pw in candidates:
            for cfg in pages:
                try:
                    key = AESGCM(kek(pw, base64.b64decode(cfg['salt']))).decrypt(
                        base64.b64decode(cfg['iv']), base64.b64decode(cfg['key']), None)
                    page = AESGCM(key).decrypt(blob[:12], blob[12:], None).decode('utf-8')
                except Exception:
                    continue
                return re.sub(re.escape(BUILD_START) + '.*?' + re.escape(BUILD_END), '', page, count=1, flags=re.S)
        if not sys.stdin.isatty():
            break
        old = input('Per riusare il configuratore pubblicato serve la password ATTUALE (vecchia) di un dealer qualsiasi: ').strip()
        if not old:
            break
        candidates = [old]
    sys.exit('Non riesco a decifrare app/app.enc: nessuna delle password inserite è quella attuale di un dealer. '
             'indica la cartella del configuratore, es. python3 tools/build.py engine-src')


def data_uri(rel):
    if not rel:
        return ''
    full = path(rel)
    mime = mimetypes.guess_type(full)[0] or 'application/octet-stream'
    return f'data:{mime};base64,' + b64(open(full, 'rb').read())


def js_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')


UNLOCK_PAGE = r'''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><meta name="viewport" content="width=device-width,initial-scale=1"><title>xFarm — Configuratore preventivi</title>
<style>body{margin:0;font:16px -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f4f5f2;color:#333;display:flex;min-height:100vh;align-items:center;justify-content:center}form{background:#fff;padding:28px 32px;border-radius:14px;box-shadow:0 1px 8px rgba(0,0,0,.08);width:100%;max-width:360px;box-sizing:border-box;margin:16px}h1{font-size:18px;margin:0 0 6px}p{margin:0 0 16px;color:#555;font-size:14px}input{width:100%;box-sizing:border-box;font:inherit;padding:10px 12px;border:1px solid #ccc;border-radius:8px;margin-bottom:12px}button{width:100%;font:inherit;font-weight:600;padding:10px;border:0;border-radius:8px;background:#2e7d32;color:#fff;cursor:pointer}button:disabled{opacity:.6;cursor:wait}#m{color:#c62828;margin:12px 0 0;min-height:1em}</style>
__GOATCOUNTER__<script id="qx-cfg" type="application/json">__CFG__</script>
</head><body>
<form id="f" autocomplete="on"><h1>xFarm Technologies</h1><p>Configuratore preventivi. Inserisci la password che ti ha dato xFarm.</p>
<input type="text" name="username" value="__SLUG__" autocomplete="username" hidden>
<input id="p" type="password" autocomplete="current-password" placeholder="Password" aria-label="Password" required autofocus>
<button id="b" type="submit">Apri il configuratore</button><p id="m" role="alert"></p></form>
<script>
(function () {
  'use strict';
  var C = JSON.parse(document.getElementById('qx-cfg').textContent);
  var SK = 'qxKey:' + C.slug;
  var f = document.getElementById('f'), inp = document.getElementById('p'),
      btn = document.getElementById('b'), msg = document.getElementById('m');
  function un64(s) { var b = atob(s), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }
  function to64(u) { var s = ''; for (var i = 0; i < u.length; i++) s += String.fromCharCode(u[i]); return btoa(s); }
  function store(k, v) { try { if (v) sessionStorage.setItem(k, v); else sessionStorage.removeItem(k); } catch (e) {} }
  function stored(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function busy(on, text) { btn.disabled = on; inp.disabled = on; msg.textContent = text || ''; msg.style.color = on ? '#555' : ''; }

  async function unwrap(password) {
    var base = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveKey']);
    var kek = await crypto.subtle.deriveKey({ name: 'PBKDF2', hash: 'SHA-256', salt: un64(C.salt), iterations: C.iterations },
      base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    return new Uint8Array(await crypto.subtle.decrypt({ name: 'AES-GCM', iv: un64(C.iv) }, kek, un64(C.key)));
  }

  async function openApp(raw) {
    var key = await crypto.subtle.importKey('raw', raw, 'AES-GCM', false, ['decrypt']);
    var r = await fetch('../app/app.enc?v=' + C.build, { cache: 'no-cache' });
    if (!r.ok) throw new Error('download');
    var buf = new Uint8Array(await r.arrayBuffer()), pt;
    try { pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: buf.slice(0, 12) }, key, buf.slice(12)); }
    catch (e) { throw new Error('stale'); }
    var page = new TextDecoder().decode(pt);
    var head = '<base href="../app/"><script>window.QX_DEALER_SLUG=' + JSON.stringify(C.slug) + ';<\/script>';
    page = /<head[^>]*>/i.test(page) ? page.replace(/<head[^>]*>/i, function (m) { return m + head; }) : head + page;
    document.open(); document.write(page); document.close();
  }

  function fail(e) {
    busy(false, e && e.message === 'stale'
      ? 'Il configuratore è stato aggiornato: ricarica la pagina.'
      : 'Impossibile aprire il configuratore. Controlla la connessione e riprova.');
  }

  f.addEventListener('submit', async function (ev) {
    ev.preventDefault();
    busy(true, 'Verifica in corso…');
    var raw;
    try { raw = await unwrap(inp.value); }
    catch (e) { busy(false, 'Password non corretta.'); inp.select(); return; }
    store(SK, to64(raw));
    try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: '/' + C.slug + '/aperto', title: C.slug + ' aperto', event: true }); } catch (e) {}
    busy(true, 'Apertura del configuratore…');
    try { await openApp(raw); } catch (e) { store(SK, null); fail(e); }
  });

  if (!window.crypto || !crypto.subtle) { busy(true, 'Questo browser non è supportato: usa una versione recente di Chrome, Edge, Safari o Firefox.'); return; }
  var saved = stored(SK);
  if (saved) {
    busy(true, 'Apertura del configuratore…');
    openApp(un64(saved)).catch(function () { store(SK, null); busy(false); inp.focus(); });
  }
})();
</script>
</body></html>
'''


def unlock_page(slug, cfg, goatcounter):
    gc = ''
    if goatcounter:
        gc = (f'<script data-goatcounter="https://{html.escape(goatcounter)}.goatcounter.com/count" '
              f'async src="https://gc.zgo.at/count.js"></script>\n')
    return (UNLOCK_PAGE.replace('__GOATCOUNTER__', gc)
            .replace('__CFG__', js_json(cfg))
            .replace('__SLUG__', html.escape(slug)))


def readme_table(site, dealers):
    base = site['base_url'].rstrip('/') + '/'
    rows = ['| Dealer | Link | Logo |', '|---|---|---|']
    for slug, d in dealers.items():
        logo = 'solo xFarm (generico)' if d.get('generico') else (f'[{os.path.basename(d["logo"])}]({d["logo"]})' if d.get('logo') else '—')
        rows.append(f'| {d["name"]} | {base}{slug}/ | {logo} |')
    return '\n'.join(rows)


def update_readme(table):
    p = path('README.md')
    s = open(p, encoding='utf-8').read()
    block = f'{TABLE_START}\n{table}\n{TABLE_END}'
    if TABLE_START in s and TABLE_END in s:
        s = re.sub(re.escape(TABLE_START) + '.*?' + re.escape(TABLE_END), lambda m: block, s, count=1, flags=re.S)
    else:
        s = s.rstrip() + '\n\n' + block + '\n'
    open(p, 'w', encoding='utf-8').write(s)


def main():
    site = read_json('site.json')
    dealers = read_json('dealers.json')
    passwords = ask_passwords(dealers)

    if os.path.exists(path('passwords.json')):
        os.remove(path('passwords.json'))  # le password non devono stare nel repository

    # 1. configuratore in chiaro: nuova sorgente oppure recupero da app.enc
    if len(sys.argv) > 1:
        src = sys.argv[1]
        page = open(os.path.join(src, 'index.html'), encoding='utf-8').read()
        os.makedirs(path('app', 'assets'), exist_ok=True)
        src_assets = os.path.join(src, 'assets')
        if os.path.isdir(src_assets):
            for f in os.listdir(src_assets):
                shutil.copyfile(os.path.join(src_assets, f), path('app', 'assets', f))
    else:
        page = recover_source(passwords)

    # 2. dati dei dealer dentro la parte cifrata (loghi come data URI)
    qx_dealers = {s: {'name': d['name'], 'lang': d.get('lang', 'it'),
                      'logo': '' if d.get('generico') else data_uri(d.get('logo', '')),
                      'generico': bool(d.get('generico'))} for s, d in dealers.items()}
    page = page.replace('const QX_LOGO_B64 =', 'var QX_LOGO_B64 =', 1)
    inject = (f'{BUILD_START}<script>window.QX_DEALERS = {js_json(qx_dealers)};</script>'
              f'<script src="brand.js"></script>{BUILD_END}')
    i = page.rfind('</body>')
    page = page[:i] + inject + page[i:] if i > 0 else page + inject

    # 3. cifratura del configuratore con una chiave nuova
    key, iv = AESGCM.generate_key(bit_length=256), secrets.token_bytes(12)
    blob = iv + AESGCM(key).encrypt(iv, page.encode('utf-8'), None)
    open(path('app', 'app.enc'), 'wb').write(blob)
    build = hashlib.sha256(blob).hexdigest()[:12]
    for old in ('app/index.html', 'dealers.js'):
        if os.path.exists(path(old)):
            os.remove(path(old))

    # 4. una pagina con password per ogni dealer
    for slug in dealers:
        salt, wiv = secrets.token_bytes(16), secrets.token_bytes(12)
        cfg = {'slug': slug, 'build': build, 'iterations': ITERATIONS, 'salt': b64(salt), 'iv': b64(wiv),
               'key': b64(AESGCM(kek(passwords[slug], salt)).encrypt(wiv, key, None))}
        os.makedirs(path(slug), exist_ok=True)
        open(path(slug, 'index.html'), 'w', encoding='utf-8').write(unlock_page(slug, cfg, site.get('goatcounter')))

    # 5. cartelle di dealer non più in dealers.json
    removed = [n for n in sorted(os.listdir(ROOT)) if n not in dealers and page_config(n)]
    for n in removed:
        shutil.rmtree(path(n))

    # 6. tabella nel README
    update_readme(readme_table(site, dealers))

    print('Fatto:', ', '.join(dealers))
    if removed:
        print('Cartelle eliminate:', ', '.join(removed))


if __name__ == '__main__':
    main()
