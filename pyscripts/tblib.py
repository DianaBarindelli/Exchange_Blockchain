#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from brownie import accounts, web3, network, Wei
from terminaltables import AsciiTable
import math
from colorama import Fore
from termcolor import colored  #'install colorama'
import random
import threading
import time
from enum import Enum

"""
`tblib.py` è la trading_bots_library sulla quale sono presenti tutte le funzioni necessarie per il funzionamento di `test_bot_automation.py`.
Non preoccuparti se non funziona sul tuo PC: si tratta di un test e alcune dipendenze potrebbero non essere installate sulla
tua macchina locale.
E' necessario installare la libreria colorama `conda install -c anaconda colorama` su Anaconda.
E' necessario avere il file `test_bot_automation.py` nella stessa cartella `scripts` del progetto `ganache_test`.
E' necessario avere `Faucet.sol` , `Pool.sol` e `Token.sol` nella cartella `contracts` del progetto.
"""


def random_exclude(excluded,max):
    """
    Lo uso per estrarre la seconda pool escludendo la prima nel metodo `.randomize()` della classe `market_op`. 
    """
    extracted=excluded

    while extracted == excluded:

        extracted = random.randint(0,max-1)
    
    return extracted

def establish_connection(network_selected):
    """
    Prova a stabilire una connessione con il network indicato da `network_selected`.

    `network_selected`: str - network selezionato
    """
    try:
        print(f'Connecting to {network_selected} network, please wait...')
        print(network.show_active())
        network.connect(network_selected)
        print('Connection estabilished.')
    except:
        print('Connection error, retrying without launching RPC')
        network.connect(network_selected, launch_rpc=False)

def ether(wei_number):
    """
    Data una quantità di wei la trasforma in ether

    `wei_number`: int - numero di wei da trasformare in ether
    """
    return wei_number/Wei('1 ether')

def gwei(wei_number):
    """
    Data una quantità di wei la trasforma in gwei

    `wei_number`: int - numero di wei da trasformare in gwei
    """
    return wei_number/Wei('1 gwei')

def get_gas_price():
    """
    Gets actual gas price and sets it for the next transactions in the network.
    Sets max amount of gas per transaction as well
    """
    #PER MATTEO: lui aggiunge sempre un gwei. Non capisco, so far non lo faccio, da vedere se farlo o meno
    gas_price=web3.eth.gasPrice
    increase=0.4*gas_price  #10%
    gas_price+=increase
    print(f"Gas price: {gwei(gas_price)} gwei")
    network.gas_price(f'{gas_price} wei')   #this sets the gas price for the next transactions
    network.gas_limit(300000)               #this sets the MAX amount of gas per transaction. WARNING
    return gas_price

def sigmoid(x):
    """
    Funzione a gradino compresa tra [0,1].

    `x`: double 
    """
    return 0.5 * (x / math.sqrt(x ** 2 + 1) + 1) 

def randamount():
    """
    Questa serve per estrarre una quantità [0,1] con un criterio gaussiano usando la sigmoide di cui sopra
    """
    return sigmoid(random.gauss(-1, 0.5)) 

def buy(paycoin,pool, amount, account, gas_price):
    """
    Compra il token di una certa pool in cambio di paycoin.
    L'allowance dell'account deve essere 1.05 volte il prezzo attutale, in modo che l'operazione viene comunque eseguita 
    nel momento in cui il prezzo varia.
    Se non ha l'allowance questa viene aumentata con approve. Si collega in tutto alla funzione `buyToken` della pool.

    `paycoin`: Contract - variabile contratto del paycoin dell'esame
    `pool`: Contract - variabile contratto della pool del token che si vuole comprare.
    `amount`: int - numero di token che si vuole comprare in termini di 10**18.
    `account`: account - l'account con il quale fare l'operazione. Sarà uno dei bot.
    `gas_price`: prezzo del gas che si vuole usare. Per le operazioni dei bot forse meglio automatico.
                 calcolarlo con `web3.eth.gasPrice` 
    """
    try:
        if paycoin.allowance(account, pool) < 1.05*pool.Get_Token_Price(amount):  
            paycoin.approve(pool, pool.Get_Token_Price(amount)*1.05, {'from': account, 'gas_price': gas_price})
        pool.buy(amount, {'from': account, 'gas_price': gas_price})
    except:
        print(colored('Unable to buy, something went wrong (sudden price change?)','red'))
        pass


def sell(pool, token, amount, account,gas_price):
    """
    Vende il token di una certa `pool` in cambio di Paycoin.
    Anche qui si imposta l'allowance in modo che sia 1.05 volte il prezzo attuale per far sì che l'operazione non venga 
    interrotta da piccole oscillazioni del prezzo di mercato.
    
    `pool`: Contract - variabile contratto della pool del token che si vuole vendere.
    `token`: Contract - variabile contratto del token associato ad una certa pool.
    `amount`: int - numero di token che si vuole vendere in termini di 10**18.
    `account`: account - l'account con il quale fare l'operazione. Sarà uno dei bot.
    `gas_price`: prezzo del gas che si vuole usare. Per le operazioni dei bot forse meglio automatico.
                 calcolarlo con `web3.eth.gasPrice` 
    """
   
    try:
        if token.allowance(account, pool) < 1.05*amount:
            token.approve(pool, amount*1.05, {'from': account, 'gas_price': gas_price})
        pool.sell(amount, {'from': account, 'gas_price': gas_price})
    except: 
        print(colored('Unable to sell, something went wrog (sudden price change?)','red'))
        pass

def swap(pool1, pool2, token, amount, account,gas_price):
    """
    Scambia il token relativo a pool1 (che si possiede) con quello relativo a pool2 (che si vuole acquisire).
    Anche qui si imposta l'allowance in modo che sia 1.05 volte il prezzo attuale, calcolato con `getSwapPrice`
    per far sì che l'operazione non venga 
    interrotta da piccole oscillazioni del prezzo di mercato.
    
    `pool1`: Contract - variabile contratto della pool del token che di cui si è in possesso e si vuole scambiare.
    `pool2`: Contract - variabile contratto della pool del token che si vuole acquisire.
    `token`: Contract - variabile contratto del token associato ad una certa pool.
    `amount`: int - numero di token che si vuole acquisire in termini di 10**18.
    `account`: account - l'account con il quale fare l'operazione. Sarà uno dei bot.
    `gas_price`: prezzo del gas che si vuole usare. Per le operazioni dei bot forse meglio automatico.
                 calcolarlo con `web3.eth.gasPrice` 
    """

    try:
        if token.allowance(account, pool1) < pool1.get_swap_price(pool2, amount)*1.05:
            token.approve(pool1, pool1.get_swap_price(pool2, amount)*1.05, {'from': account, 'gas_price': gas_price})
        pool1.swap(pool2, amount, {'from': account, 'gas_price': gas_price})

    except:  
        print(colored( 'unable to swapp, something went wrong (sudden price change?)','red'))
        pass

def get_lambda(mean_time):
    """
    Dato un tempo medio di attesa che vogliamo ottenere per la distribuzione, restituisce il corretto lamda da impostare.
    Ovviamente la relazione è immediata ma permette di pensare direttamente al tempo medio.
    `mean time`: double - tempo medio di attesa che si vuole ottenere
    """
    return 1/mean_time

class market_op():
    """
    Classe che rappresenta una operazione da parte di un bot.
    """

    def __init__(self,nbots,pools,Actions,mean_time):
        """
        Costruzione della classe.
        `nbots`: int - numero di bot tra cui scegliere
        `pools`: list - pool tra le quali scegliere
        `Actions`: Enum - lista delle azioni che si possono fare
        `mean_time`: Tempo medio che si vuole attendere tra una operazione e l'altra
        """
        
        self.nbots = nbots
        self.pools = pools
        self.Actions = Actions
        self.mean_time = mean_time

    def randomize(self):
        """
        Estrae a random il bot che farà l'operazione, la pool nella quale verrà fatta l'operazione,l'operazione che verrà fatta
        e quando verrà fatta. Importante, altrimenti avremmo troppe richieste.
        """
        self.bot_number=random.randint(0,self.nbots-1)       #è il numero del bot, da non confondere con `account`
        self.pool_number=random.randint(0,len(self.pools)-1)
        self.pool_number2=random_exclude(self.pool_number,len(self.pools))
        self.action=random.choice([self.Actions.buy,self.Actions.sell,self.Actions.swap])
        self.time=random.expovariate(get_lambda(self.mean_time))

    def config(self,pools,tokens,token_names,token_symbols,bots):
        """
        Configura l'oggetto `market_op` rendendo variabili interne i contratti e i simboli e stampa un po' di info.
        `pools`: list - pool tra le quali scegliere
        `tokens`: list - token tra le quali scegliere
        `token_names`: list - pool tra le quali scegliere
        `token_symbols`: list - pool tra le quali scegliere
        `bots`: list - lista dei bot allocati
        """
        self.pool=pools[self.pool_number]
        self.pool2=pools[self.pool_number2]
        self.token=tokens[self.pool_number]
        self.token_name=token_names[self.pool_number]
        self.token_symbol=token_symbols[self.pool_number]
        self.token_symbol2=token_symbols[self.pool_number2]
        self.account=bots[self.bot_number]
        
        print(f'chosen Bot #{self.bot_number}')
        print(f'******* Bot #{self.bot_number} balance: {ether(self.account.balance())} eth')
        print(f'******* Bot #{self.bot_number} pool [#{self.pool_number}] balance: {ether(self.token.balanceOf(self.account))} {self.token_symbol}')

    def buy(self,paycoin,gas_price):
        """
        Esegue l'operazione di acquisito secondo le variabili estratte e utilizzando il paycoin. Usa la funzione `buy` scritta sopra
        `paycoin`: Contract - token di pagamento.
        `gas_price`: prezzo del gas che si vuole usare. Per le operazioni dei bot forse meglio automatico.
                 calcolarlo con `web3.eth.gasPrice`.

        return: bool - Flag che indica se l'operazione è andata a buon fine o meno
        """
        amount_in_paycoin=paycoin.balanceOf(self.account)*randamount()*0.3
        try:

            if amount_in_paycoin == 0:                  #Accade se il conto in ether è vuoto. Non dovrebbe accadere se si fa il topup
                
                raise ValueError

            amount=self.pool.How_Many_Token(amount_in_paycoin)   
            print(f'******* Bot #{self.bot_number} is buying {ether(amount)} {self.token_symbol} tokens for {ether(amount_in_paycoin)} PcN')
            threading.Thread(target=buy, args=(paycoin,self.pool,amount,self.account,gas_price)).start()
            return True

        except ValueError:

            print(f'******* Bot #{self.bot_number} unable to trade {ether(amount_in_paycoin)} PcN with {self.token_symbol}')
            return False

    def sell(self,gas_price):
        """
        Esegue l'operazione di vendita secondo le variabili estratte. Usa la funzione `sell` scritta sopra.
        `gas_price`: prezzo del gas che si vuole usare. Per le operazioni dei bot forse meglio automatico.
                 calcolarlo con `web3.eth.gasPrice`.

        return: bool - Flag che indica se l'operazione è andata a buon fine o meno
        """

        amount_in_token= self.token.balanceOf(self.account)*randamount()*0.3
        try:
        
            if amount_in_token==0:                  #Accade se ha il balance di token vuoto

                raise ValueError

            _=self.pool.Get_Token_Price(amount_in_token)       #credo calcoli quanti paycoin ti dà, se troppo alto per la pool fallisce
            print(f'******* Bot #{self.bot_number} is selling {ether(amount_in_token)} {self.token_symbol} tokens')
            threading.Thread(target=sell,args=(self.pool,self.token,amount_in_token,self.account,gas_price)).start()
            return True

        except ValueError:

            print(f'******* Bot #{self.bot_number} unable to sell {ether(amount_in_token)} {self.token_symbol}')
            return False

    def swap(self,gas_price):
        """
        Esegue l'operazione di scambio dei token secondo le variabili estratte. Usa la funzione `swap` scritta sopra sopra
        self.pool è il token che detiene e sarà scambiato mentre self.pool2 è quello che voglio acquisire
        `gas_price`: prezzo del gas che si vuole usare. Per le operazioni dei bot forse meglio automatico.
                 calcolarlo con `web3.eth.gasPrice`.

        return: bool - Flag che indica se l'operazione è andata a buon fine o meno
        """

        amount_in_token1=self.token.balanceOf(self.account) * randamount() *0.3     #Questo calcola a caso una quantità di token 1 al massimo il 30% del suo portafoglio
                                                                                #che il bot scambierà

        try:

            if amount_in_token1 == 0:                                           #Accade se ha il balance di token vuoto

                raise ValueError

            amount=self.pool2.How_Many_Token(self.pool.Get_Token_Price(amount_in_token1))  #il numero dei token 2 che si riesce a comprare è calcolato sul valore in paycoin del token 1
            print(f'******* Bot #{self.bot_number} is swapping {ether(amount_in_token1)} {self.token_symbol} tokens for {ether(amount)} {self.token_symbol2} tokens.')
            threading.Thread(target=swap, args=(self.pool,self.pool2,self.token,amount,self.account,gas_price)).start()                                                                                
            return True
        
        except ValueError:

            print(f'******* Bot #{self.bot_number} unable to swap {ether(amount_in_token1)} {self.token_symbol}')
            return False



class ATM():
    """
    Classe che serve per ricaricare i bot. Sia quando questi vengono caricati inizialmente dove verranno ricaricati dal
    minter dei paycoin e dallo stesso in termini di eth, sia quando dopo un certo numero di operazioni avranno finito le
    risorse e necessiteranno di un topup e prenderenno questi soldi da un Faucet.
    """

    def __init__(self,bots,paycoin_minter,faucet,paycoin,Tokens,Token_symbols,pools):
        """
        Costruzione della classe.
        `bots`: list - lista dei bot
        `paycoin_minter`: addr - minter del contratto paycoin
        `faucet`: contract - contratto tipo faucet da cui nel corso della giornata i bot attingeranno
        `paycoin`: contract - contratto del token di paycoin

        """
        
        self.bots = bots
        self.paycoin_minter = paycoin_minter
        self.faucet = faucet
        self.paycoin = paycoin
        self.Tokens=Tokens
        self.pools=pools
        self.Token_symbols=Token_symbols

    def initial_topup(self,eth_limit=5*10**15):

        """
        Ricarica di credito che si effettua all'inizio quando c'è appena stato il deploy degli smart contract. Avverrà una
        volta sola nel corso dell'esame.
        `eth_limit`: int - soglia di eth al di sotto della quale scatta la ricarica

        IMPORTANTE: ogni operazione fallirà non appena il conto è inferiore di max_gas_limit*gas_price + value. Quello che conta
        è appunto il max_gas_limit.
        'Per 100 bot inizialmente vengono caricati 0.5 eth'
        """

        print('Filling up the bots with paycoins:')
        thr=[]
        ethlimit=eth_limit                                #(0.001 eth)

        for botno, bot in enumerate(self.bots):
    
            print(f'Stocking up bot [{botno}] {bot}')
        
            #Ricarica di ether per le gas fee
            #ATTENZIONE: LEGGI COMMENTO SI PUò FORSE IMPLEMENTARE MENGLIO
            if  bot.balance() < ethlimit:      

                thr.append(threading.Thread(target=self.paycoin_minter.transfer, args=(bot, ethlimit - bot.balance())))     #questa è da capire. Così rischio di spendere davvero tante fee. potrei ricaricarlo per fare un tot di operazioni calcolando quante ne faccio in media.
                thr[-1].start()
        
            time.sleep(1)       #Aspetta un secondo altrimenti fa troppe transazioni
    
        for t in thr:
            t.join()            #Aspetta che tutte le richieste fatte vengano eseguite

        print('\nDone procedures\n')

    def eth_pcn_balances(self):
        """
        stampa i balances in eth di tutti i bot.
        """
        for botno, bot in enumerate(self.bots):
            print('> Bot # ',botno, 'ETH BALANCE', ether(bot.balance()),' eth' )

    def balances(self):
        """
        stampa i balances completi di tutti i bot.
        """
        for botno, bot in enumerate(self.bots):
            print('\n> Bot # ',botno, 'ETH BALANCE', ether(bot.balance()),' eth' )
            
            print('> Bot # ',botno, ' PcN BALANCE', ether(self.paycoin.balanceOf(bot)),' PcN' )
            for i in range(0,len(self.Tokens)):
                print('> Bot # ',botno, f' {self.Token_symbols[i]} BALANCE', ether(self.Tokens[i].balanceOf(bot)),f' {self.Token_symbols[i]}' )
        print(' ')   

    def market_prices (self):
        """
        Funzione che ritorna il prezzo di tutti i token associati alla classe `nourishment` in termini di PcN.

        return: list - i prezzi in PcN
        """

        starting_prices=[]

        for i in range(0,len(self.pools)):

            starting_prices.append(ether(self.pools[i].Get_Token_Price(10**18)))
            print(f'{self.Token_symbols[i]} starting price: {starting_prices[-1]} PcN')

        return starting_prices

    def market_prices_changes(self,starting_prices):
        """
        Stampa la variazione percentuale dei prezzi.
        """

        ending_prices=[]

        for i in range(0,len(self.pools)):

            ending_prices.append(ether(self.pools[i].Get_Token_Price(10**18)))
            print(f'{self.Token_symbols[i]} ending price: {ending_prices[-1]} PcN')
            print(f'{self.Token_symbols[i]} variation: {(((ending_prices[-1]-starting_prices[i])/starting_prices[i]))*100}%')

    def topup(self,account,gas_price):
        """
        Funzione che ricarica il balance del bot nel momento in cui questo è al di sotto di una certa soglia definita da 
        `limit`.

        `account`: account - l'account con il quale fare l'operazione. Sarà uno dei bot.
        `faucet`: Contract - contratto del faucet a cui si fa riferimento. Accetta withdraw dei bot.
        `gas_price`: prezzo del gas che si vuole usare. Per le operazioni dei bot forse meglio automatico.
                 calcolarlo con `web3.eth.gasPrice` 
        """

        limitbalance = 5*3*10**5 * gas_price                           #soglia sotto la quale il bot rischia di non far eseguire una transazione. E' uguale a 5 volte la massima fee accettata per transazione (VEDI `set_gas_price()`)


        if account.balance() < limitbalance:

            withdrawamount = 2*(limitbalance - account.balance())
            print(colored('\nINSIDE_TOPUP\n','red', 'on_green'))
            print(f'Bot balance is under threshold, withdrawing from faucet : {ether(withdrawamount)} eth')
            print(f'{gwei(gas_price)} gwei')
            print(f'{ether(10**6*gas_price)} eth')
            withdrawamount += 0.1*withdrawamount*randamount()                   # Adds a bit of randomness
            print(f'Bot balance is under threshold, withdrawing from faucet : {ether(withdrawamount)} eth')
            self.faucet.withdraw(withdrawamount, {'from': account})
            print(f'Now the balance is {ether(account.balance())} Gwei')

def run_noise_bots(personal_account,bots,pools,tokens,mean_time,token_names,token_symbols,bot_ATM,Paycoin):
    """
    Programma che fa andare gli scambi automatici dei bot una volta riempiti inizialmente gli account.

    `personal_account`: addr - personal account
    `bots`: list - lista dei bot creati tramite mnemonic e ricaricati con opportuni ether e paycoin tramite la classe `ATM`
    `pools`: list - lista delle pools
    `tokens`: list - lista dei token
    `mean_time`: int - tempo medio di attesa tra due transazioni (se inferiore al secondo il programma va in ALT)
    `token_names`: list - lista dei nomi dei token
    `token_symbols`: list - lista dei simboli dei token
    `bot_ATM`: object - oggetto della classe ATM, serve per ricaricare i bot di PcN e Eth e stampare i balances vari.
    `Paycoin`: Contract - contratto del paycoin

    """

    nbots=len(bots)
    i=0
    locks=[threading.Lock() for bot in bots]      #risolve la race condition: thread che modificano simultaneamnete la stessa
                                                  #cosa in modi diversi.
    Actions= Enum('Actions', 'buy sell swap')   #Ad ognuna delle tre associa un numero.
    #mean_time=1                                #voglio avere in media una operazione ogni 10s
                                                #WARNING: col fatto che le operazioni impiegano del tempo potrei doverlo 
                                                #diminuire
    operation=market_op(nbots, pools, Actions, mean_time)  #costruttore della classe

    while True:

        if bot_ATM.faucet.balance()<0.1*10**18:
            bot_ATM.faucet.deposit({'from':personal_account,'value':0.2*10**18})

        gas_price=get_gas_price()

        """
        Step1: estrazione casuale dell'operazione.
        -)estrarre a random il bot che farà l'operazione
        -)estrarre a random la pool nella quale verrà fatta l'operazione
        -)estrarre a random l'operazione che verrà fatta
        -)estrarre quando verrà fatta. Importante, altrimenti avremmo troppe richieste
        Lo faccio utilizzando la classe `market_op` definita in tblib
        """

        op=0
        operation.randomize()                                           #estrae le varie features
        success = locks[operation.bot_number].acquire(timeout=0.01)     #crea il lock sul thread per al massimo un tempo t=0

        """
        A questo punto definisco tutti i token e le pool che sono state estratte e controllo che il bot abbia i fondi
        necessari.
        """

        if success:

            operation.config(pools,tokens,token_names,token_symbols,bots)
            bot_ATM.topup(operation.account,gas_price)                          #check if bot balance is enough to carry out the operation

            """
            A seconda dell'operazione estratta bisogna ora realizzarla utilizzando i metodi della classe `market_op`
            """

            if operation.action == Actions.buy:
                op='buy'
                success=operation.buy(Paycoin,gas_price)
                

            elif operation.action == Actions.sell:
                op='sell'
                success=operation.sell(gas_price)

            elif operation.action == Actions.swap:
                op='swap'
                success=operation.swap(gas_price)

            locks[operation.bot_number].release()           #rilasso la condizione per evitare race condition nel threading.

            if success:
                i+=1
                print(colored(f'Carried_out_op #{i}','red','on_green'))
                time.sleep(operation.time)

        else:                                               #Lock acquire not satisfied (magari ci sta mettendo un mondo di tempo)
            
            continue                                        #ripeti

def pools_config(pools,dict_balances,tokens,users,bot_minter,Paycoin):

    """
    Minta alla pool una certa quantità di token e paycoin per quanto indicato da `dict_balances`. Successivamente termina
    la configurazione con pool.pool_Set() che imposta il `max_increase_decrease_amount` di `Pool.sol`

    `pools`: list - lista delle pools
    `dict_balances`: dict - dizionario con le quantità di token (sia token che paycoin) per ogni pool
    `tokens`: list - lista dei token
    `users`: list - lista di account proprietari di pools e tokens
    `bot_minter`: account - proprietario del contratto `Faucet` e `Paycoin`
    `Paycoin`: Contract - contratto del paycoin
    
    """

    for i in range (0,len(pools)):
        
        tokens[i].mint(pools[i],dict_balances['token'][str(i+1)]*10**18, {'from':users[i]})                #Rapporto 1:1
        Paycoin.mint(pools[i],dict_balances['paycoin'][str(i+1)]*10**18, {'from':bot_minter})
        pools[i].pool_Set({'from':users[i]})

def mint_paycoin_to_bots(bots,paycoin,paycoin_minter):

    """
    Funzione che serve per dotare di paycoin per la prima volta i bot. Initial top_up della classe ATM così gestirà gli ether
    e non farà richieste inutili.
    """
        
    thr=[]
    for botno, bot in enumerate(bots):

        print(f'Stocking up bot [{botno}] {bot} with Paycoins')
        
        if paycoin.balanceOf(bot)==0:      

            PcN_amount=random.uniform (1000*10**18,100000*10**18)
            gas_price=get_gas_price()
            thr.append(threading.Thread(target=paycoin.mint, args=(bot, PcN_amount, {'from':paycoin_minter, 'gas_price':gas_price})))
            thr[-1].start()

    for t in thr:
        t.join()  

    print('All bots now have a Paycoin balance.')