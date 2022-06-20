#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from brownie.network import connect, accounts
from brownie import Contract, project, web3
import json
import random
import secrets
import os
from enum import Enum
from termcolor import colored

from tblib import ether
from tblib import establish_connection, ATM, run_noise_bots

"""
Da fare
"""

random.seed(secrets.randbits(2048))

def main():

    run_noise_bots(personal_account=personal_account,bots=bots,pools=pools,tokens=tokens,mean_time=30,token_names=token_names,
                token_symbols=token_symbols,bot_ATM=bot_ATM,Paycoin=Paycoin)
    print('everything went through')

if __name__=='__main__':

    print('\n')
    os.system('figlet -c RunningBots')       # `brew install figlet` non te ne pentirai. Altrimenti commentalo
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
    Prima di tutto carico i file json che contengono gli indirizzi e le chiavi private.

    `AddressesData`: Contiene tutti gli indirizzi dei giocatori con relative pool e token. 
    `PrivateData`: Contiene l'id personale + PK, l'id dei bot + PK, l'id dei faucet.
    
    """

    AddressesData=json.loads(open('addresses.json').read())
    PrivateData=json.loads(open('private_dict.json').read())
    
    """
    Pesco dal wallet dei bot un numero n_bots di bot per le transazioni automatiche
    """

    print('retirieving ',colored('100','red'),' bots from mnemonic, this could take a while ...')
    n_bots=100
    try:
        bots=accounts.from_mnemonic(PrivateData['bots_account']['mnemonic'], count=n_bots)

    except:
        print(colored('WARNING: ERROR OCCURRED','red'))
        exit(-1)

    """
    Recupero e connetto l'account personale dell'utente.
    """
    try:
        personal_account=accounts.from_mnemonic(PrivateData['personal_account']['mnemonic'], count=1)

    except:
        print(colored('WARNING: ADD YOUR PRIVATE ACCOUNT BIP39 MNEMONIC PHRASE','red'))
        print(colored('To retrieve your BIP39 MNEMONIC, open MetaMask with your bot account, click `MyAccounts`<`Settings`<`Security & Privacy`< `Reveal secret recovery phrase`','red'))
        print(colored('HERE\'S A BIP39 MNEMONIC EXAMPLE: "load ship usual decade human subway pen orbit midnight flag lend surround suit annual canal"','red'))
        exit(-1)

    """
    Connetto il bot_minter, ovvero il proprietario del contratto Paycoin.sol. Servirà per mintare i paycoin ai vari bot.
    """

    bot_minter=accounts.from_mnemonic(AddressesData['bot_minter']['mnemonic'],count=1)

    """
    Connetto ora i vari contratti relativi a token e pools.
    """

    print('Retrieving token contracts, please wait...')

    names=['Matteo','Diana','Francesco','Riccardo','Cristiano']

    Paycoin=Contract.from_abi("Paycoin",AddressesData['bot_minter']['paycoin'],Token.abi)
    tokens=[Contract.from_abi("Tokens",AddressesData[f'{name}']['token'], Token.abi) for name in names]
    pools=[Contract.from_abi("Tokens",AddressesData[f'{name}']['pool'], Pool.abi) for name in names]
    token_names=[AddressesData[f'{name}']['token name'] for name in names]
    token_symbols=[AddressesData[f'{name}']['token symbol'] for name in names]
        
    """
    Connetto il faucet e stampo il balance
    """

    print('Deploying and filling up faucet')
    faucet=Contract.from_abi("Faucet",PrivateData['faucet'],Faucet.abi)
    print('Faucet balance:', ether(faucet.balance()),' eth')
    
    """
    Creo un oggetto della classe `ATM`. Si occuperà di verificare che i bot abbiano il credito necessario per le varie 
    operazioni ed eventualmente di ricaricarli.
    """

    bot_ATM=ATM(bots,bot_minter,faucet,Paycoin,tokens,token_symbols,pools)
    bot_ATM.initial_topup()

    """
    Stampo i valori iniziali dei vari token in termini di PcN
    """

    print('\n********************************************************************\n')
    starting_prices=bot_ATM.market_prices()
    print('\n********************************************************************\n')

    main()

    print('\n*** SCRIP HAS ENDED ***\n')

