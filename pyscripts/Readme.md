# scripts:

Qui puoi trovare la lista di tutti gli script e file `.json` che serviranno per l'esame.

### contenuto:

- `initial_deploy.py`: Per utilizzare questo file si vedano le istruzioni nella repository `Deploy_Files`
-  `running_bots.py`: esegue operazioni di mercato casuali ogni 30s. Necessita della presenza nella cartella di `tblib.py`, `addresses.json` e `private_dict.json`.
- `Challenge_manager.py`: file baffo se vojo ...
- `tblib.py`: trading_bots_library, libreria che contiene tutte le funzioni, metodi e classi necessarie per i bot automatici che eseguono transazioni casuali.
- `interact.py`: script che offre un'interfaccia semplice per interagire con tutti gli smart contract implicati e fare le operazioni di base. ATTENZIONE: all'interno di questo script non sono state implementate strategie di GAS (il gas è quello standard) che andranno implementate privatamente.
