#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import json
from brownie.network import accounts
import os

from brownie.network import connect, accounts
from brownie import Contract, project, web3
import json
import random
import secrets
import os
from enum import Enum
from telegram import Bot
from termcolor import colored

from tblib import ether
from tblib import establish_connection, mint_paycoin_to_bots

"""
Questo programma esegue il deploy di un token e di una pool e stampa due file json: un file privato `private_dict.json`
con il tuo indizzo e chiave privata (in termini di mnemonic), l'indirizzo del faucet di cui sei propiretario,  l'indirizzo del
primo dei tuoi bot e la relativa chiave privata (in termini di mnemonic).
Il secondo file in output è `YOURNAME_public_dict.json`: questo non avendo chiavi private non contiene informazioni sensibili
e può essere condiviso pubblicamente. servirà per costruire il file `addresses.json` contente gli indirizzi di tutti gli utenti
e delle relative pool e token.

"""

if __name__=='__main__':

    print('\n')
    os.system('figlet -c InitialDeploy')       # `brew install figlet` non te ne pentirai. Altrimenti commentalo
    print('\n')

    """
    Carichiamo i progetti con tutti i file di solidity scritti.
    """

    p=project.load('../',name='firstproject')
    p.load_config()
    from brownie.project.firstproject import Pool, Token, Faucet

    """
    Connetto a ropsten e imposto il gas.
    """
    establish_connection('ropsten')

    """
    Carico i file .json dove sono scritte le proporzioni delle varie pool per tutti gli utenti. Carico inoltre il json con il
    mnemonic e id del bot minter + paycoin addr
    """

    BotMinterData=json.loads(open('Bot_Minter_Data.json').read())
    StartingRatios=json.loads(open('Starting_Pool_Ratios.json').read())

    """
    Viene richiesto il mnemonic dell'account personale e dell'account con il quale si costruiscono i 100 bot
    """

    PAmnemonic=input('Please enter your PRIVATE ACCOUNT mnemonic: ')
    BAmnemonic=input('Please enter your BOTS ACCOUNT mnemonic: ')
    print('Loading 100 bots, this could take a while...')
    bots=accounts.from_mnemonic(BAmnemonic,count=100)
    
    try:    
        Paycoin_addr=BotMinterData['bot_minter']['paycoin']
    except:
        print(colored('WARNING: add Paycoin contract address','red'))

    try:
        personal_account=accounts.from_mnemonic(PAmnemonic, count=1)
        bot_minter=accounts.from_mnemonic(BotMinterData['bot_minter']['mnemonic'],count=1)
        print('Account loaded: ', personal_account)
        print('Account balance: ', ether(personal_account.balance()), ' eth')

    except:
        print(colored('WARNING: ADD YOUR BIP39 MNEMONIC PHRASE','red'))
        print(colored('To retrieve your BIP39 MNEMONIC, open MetaMask with your bot account, click `MyAccounts`<`Settings`<`Security & Privacy`< `Reveal secret recovery phrase`','red'))
        print(colored('HERE\'S A BIP39 MNEMONIC EXAMPLE: "load ship usual decade human subway pen orbit midnight flag lend surround suit annual canal"','red'))
        exit(-1)

    """
    Collego il contratto paycoin & l'account bot_minter in modo da poterci interagire
    """

    Paycoin=Contract.from_abi("Paycoin",Paycoin_addr, Token.abi)

    """
    Chiedo in input nome e simbolo del token. Faccio poi il deploy del token e della pool.
    """

    token_name=input('Please input token name (e.g. `Ragublo`): ')
    token_symbol=input('Plese enter a 3-digit token sybol (e.g. `RgB`): ')
    token=Token.deploy(f"{token_name}", f"{token_symbol}", 18, {'from':personal_account})
    pool=Pool.deploy(token,Paycoin,{'from':personal_account})

    """
    Minto alla pool una certa quantità di PcN e TkNs a seconda di quanto stabilito inizialmente.
    Minto anche all'utente il 5% della liquidità iniziale della pool
    """
        
    token.mint(pool,StartingRatios['token'][f'{personal_account}']*10**18,{'from':personal_account})
    token.mint(personal_account,0.05*StartingRatios['token'][f'{personal_account}']*10**18,{'from':personal_account})       
    Paycoin.mint(pool,StartingRatios['paycoin'][f'{personal_account}']*10**18, {'from':bot_minter})
    pool.pool_Set({'from':personal_account})

    """
    Eseguo il deploy di un contratto Faucet al quale i bot attingeranno in maniera autonoma se durante le operazioni auto
    matiche di scambio rimangono a secco.
    """

    faucet=Faucet.deploy({'from': personal_account})
    faucet.deposit({'from':personal_account,'value':0.2*10**18})
    print('Faucet balance:', ether(faucet.balance()),' eth')

    """
    Minto ai bot il loro saldo di Paycoin. Da questo momento in poi non verranno più ricaricati di paycoin ma solo di eth
    """

    mint_paycoin_to_bots(bots,Paycoin,bot_minter)

    """
    Stampo ora due file .json 
    """

    name=input('Please enter your name: ')

    public_dict={

        f'{name}':{

            'id': f'{personal_account}',
            'token': f'{token}',
            'pool':f'{pool}',
            'token name': f'{token_name}',
            'token symbol': f'{token_symbol}'
        }

    }

    private_dict={

        'personal_account':{

            'id':f'{personal_account}',
            'mnemonic': f'{PAmnemonic}',
        },

        'faucet':{

            'id':f'{faucet}'
        },

        'bots_account':{
            'id': f'{bots[0]}',
            'mnemonic': f'{BAmnemonic}'
        }
    }

    with open(f'{name}_public_dict.json','w') as public_dict_file:
        json.dump(public_dict,public_dict_file)

    with open(f'private_dict.json','w') as private_dict_file:
        json.dump(private_dict,private_dict_file)   