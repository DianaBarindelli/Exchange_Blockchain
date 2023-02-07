# Exchange
Exchange Project for Unimi Blockchain course

### Istruzioni maybe utili:
Installing OpenZeppelin version 2.5.0 (se hai Brownie) : brownie pm install OpenZeppelin/openzeppelin-contracts@2.5.0

### TODO:

- spostare i file neòlle cartelle script & contracts
- scrivere e controllare che tutti gli script peschino i file nella maniera corretta e che funzioni su tutti i pc
- scrivere bene le istruzioni
- controllare che il challenge.sol di cri funzioni con i problemi di import di solc di teo
- fare il blocco di minting 10% della liquidità al giorno 
-aggiungere il bot minter in challange.sol
- verificare la questione di token multipli di infura (se console o cartelle) + verificare gli accessi dei bot EDIT: funziona. Basta aprire terminali diversi e fare export WEB3_.... con l'id diverso, si collegherà al diverso progetto anche se sono file nella stessa cartella.
- verificare il nuovo initial deploy funzioni (con paycoin.balance ==0)
- Controllare che funzioni TimeMarket.sol
- Spostare in una cartella scripts < Deploy i file che serviranno per il deploy ed importare tutti i file.json eh,,,
                                        
                                          
### Da verificare quando facciamo il deploy:
                                          
- 1 operazione ogni 20 secondi crea troppo delirio? troppo poco?
- il fatto che il bot può allocare al massimo il 30% del suo patrimonio fa variare troppo poco i prezzi ? (alla lunga congela il mercato?)
- verificare che tutti abbiano le dipendenze e librerie installate correttamente (colorama, figlet, etc...
