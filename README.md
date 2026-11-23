# xFarm Configurator — link dealer

Configuratore xFarm co-brandizzato: ogni dealer ha il suo link personale, protetto da password. Listino unico, uguale per tutti. Il link `/xfarm/` è quello generico, con il solo logo xFarm.

Sito: https://quoteconfigurator.github.io/

## Link e credenziali

Tabella generata da `tools/build.py` (da `dealers.json`): non modificarla a mano. Le password **non** sono nel repository: le conosce solo chi gestisce il sito.

<!-- DEALERS:START -->
| Dealer | Link | Logo |
|---|---|---|
| AgriDemo Nord | https://quoteconfigurator.github.io/agri-demo-nord/ | [agri-demo-nord.svg](loghi/agri-demo-nord.svg) |
| VerdeDemo Sud | https://quoteconfigurator.github.io/verde-demo-sud/ | [verde-demo-sud.svg](loghi/verde-demo-sud.svg) |
| CampoDemo Est | https://quoteconfigurator.github.io/campo-demo-est/ | [campo-demo-est.svg](loghi/campo-demo-est.svg) |
| xFarm | https://quoteconfigurator.github.io/xfarm/ | solo xFarm (generico) |
<!-- DEALERS:END -->

## Come funziona

- Il configuratore (con il listino) è pubblicato solo cifrato, in `app/app.enc` (AES-256-GCM, chiave nuova a ogni build).
- Ogni link dealer apre una pagina che chiede la password. Con quella giusta la pagina sblocca la chiave, scarica e apre il configuratore con il logo del dealer.
- Le aperture si contano su GoatCounter, separate per dealer.

Aggiungere un dealer, cambiare una password, aggiornare il configuratore, vedere le statistiche: [LEGGIMI.md](LEGGIMI.md).
