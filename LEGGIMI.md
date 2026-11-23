# Configuratore xFarm per i dealer — sito GitHub Pages

Un solo sito con un link per ogni dealer, protetto da password. Ogni link apre il configuratore xFarm ufficiale con il logo xFarm e quello del dealer; il link generico `/xfarm/` mostra solo il logo xFarm. Il listino è lo stesso per tutti.

I link sono nella tabella del [README](README.md). Le password **non** sono nel repository (che è pubblico): le conosce solo chi gestisce il sito.

## Struttura

| File | Cosa contiene |
|---|---|
| `dealers.json` | Dealer: link (chiave), nome, logo, lingua. `"generico": true` = solo logo xFarm. |
| `passwords.local.json` | Facoltativo, **solo sul tuo computer** (escluso da git): password dei dealer, per non doverle digitare a ogni build. |
| `site.json` | Indirizzo del sito e nome dell'account GoatCounter. |
| `loghi/` | Loghi dei dealer (SVG o PNG, sfondo chiaro). Finiscono dentro la parte cifrata. |
| `app/app.enc` | Configuratore cifrato (listino e dati dei dealer). |
| `app/brand.js`, `app/assets/` | Co-branding e immagini del configuratore (non contengono prezzi). |
| `<dealer>/index.html` | Pagina con la password del dealer. Generata, non modificarla a mano. |
| `tools/build.py` | Rigenera tutto. |

Per usare `tools/build.py` serve Python 3 con la libreria `cryptography` (una volta sola: `pip install cryptography`).

## Aggiungere un dealer

1. Metti il logo in `loghi/` (SVG o PNG, sfondo chiaro).
2. Aggiungi una riga in `dealers.json`, ad esempio
   `"nuovo-dealer": {"name": "Nuovo Dealer", "logo": "loghi/nuovo-dealer.svg", "lang": "it"}`.
   La chiave (`nuovo-dealer`) diventa il link: https://quoteconfigurator.github.io/nuovo-dealer/
3. Esegui `python3 tools/build.py`. Ti chiede la password di ogni dealer (anche quella del nuovo) e aggiorna la tabella del README.
4. Fai commit e push di tutti i file cambiati. Dopo 1–2 minuti il link è online.

Per togliere un dealer: elimina la sua riga da `dealers.json` ed esegui `python3 tools/build.py` (cancella la sua cartella), poi commit e push.

## Cambiare una password

1. Esegui `python3 tools/build.py` e, quando la chiede, scrivi la password nuova del dealer (per gli altri quella di sempre).
2. Se tutte le password sono nuove, ti chiede anche una password vecchia per poter riaprire il configuratore pubblicato.
3. Commit e push.

Una password dimenticata non si può recuperare dal sito (è fatto apposta): basta impostarne una nuova con questi passi.

A ogni build il configuratore viene cifrato con una chiave nuova: la vecchia password non apre più nulla, anche se qualcuno aveva conservato la vecchia pagina. Chi era già dentro con la vecchia password deve inserire quella nuova.

## Aggiornare il configuratore (prezzi, prodotti)

Esegui `python3 tools/build.py <cartella del configuratore>`, dove la cartella contiene `index.html` e `assets/` della versione pubblicata più recente. Poi commit e push. Lo fa Claude su richiesta.

Senza cartella, `tools/build.py` riusa il configuratore già pubblicato (lo decifra con una delle password che inserisci).

Non mettere mai la cartella del configuratore in chiaro nel repository (`engine-src/` è già esclusa in `.gitignore`).

## Statistiche GoatCounter

1. Crea un account gratuito su https://www.goatcounter.com (il nome scelto diventa `<nome>.goatcounter.com`).
2. Scrivi quel nome in `site.json` al posto di `NOME-GOATCOUNTER`, esegui `python3 tools/build.py`, commit e push.
3. Apri https://<nome>.goatcounter.com. Trovi:
   - le visite alla pagina della password, separate per dealer: `/agri-demo-nord/`, `/xfarm/`, …;
   - gli eventi `/<dealer>/aperto`: le volte in cui il configuratore è stato aperto con la password giusta.

## Pubblicazione

Il sito è su GitHub Pages: repository `quoteconfigurator/quoteconfigurator.github.io`, **Settings → Pages → Deploy from a branch**, branch **main**, cartella **/ (root)**. `_config.yml` esclude dal sito i file di lavoro (README, LEGGIMI, `dealers.json`, `site.json`, `tools/`, `loghi/`).

## Cosa è pubblico

Con il piano gratuito di GitHub il repository deve essere pubblico: chiunque lo trovi su GitHub può leggere tutti i file, compresi i link dei dealer. Il listino invece è solo cifrato e le password non sono nel repository: **non scriverle mai in nessun file del repository**. Usa password non banali: chi ha il file cifrato può provare a indovinarle con calma.
