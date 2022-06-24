#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from lib2to3.pgen2 import token
from brownie.network import connect, accounts
from brownie import Contract, project, web3
import json
import threading
import secrets
import os
from enum import Enum
from termcolor import colored

from tblib import ether
from tblib import establish_connection, swap, buy, sell, get_gas_price

def operation_type(asking_string,option_list):

    temp_string=''
    for i in range(0,len(option_list)):
        temp_string+='[ '+f'{option_list[i]}'+' ]'
    request_string=asking_string+temp_string+str(': ')

    operation_type=input(request_string)
    return operation_type

def check_input_type(request_string,type_to_check):

    inputa=input(request_string)
    try:
        bool=type(float(inputa))==type_to_check
    except:
        bool=False

    return inputa,bool

if __name__=='__main__':

    print('\n')
    os.system('figlet -c Interact')       # `brew install figlet` non te ne pentirai. Altrimenti commentalo
    print('\n')

    """
    Carichiamo i progetti con tutti i file di solidity scritti.
    """

    p=project.load('../',name='firstproject')
    p.load_config()
    from brownie.project.firstproject import Pool, Token

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
    Recupero e connetto l'account personale dell'utente.
    """

    try:
        personal=accounts.from_mnemonic(PrivateData['personal_account']['mnemonic'], count=1)

    except:
        print(colored('WARNING: ADD YOUR PRIVATE ACCOUNT BIP39 MNEMONIC PHRASE','red'))
        print(colored('To retrieve your BIP39 MNEMONIC, open MetaMask with your bot account, click `MyAccounts`<`Settings`<`Security & Privacy`< `Reveal secret recovery phrase`','red'))
        print(colored('HERE\'S A BIP39 MNEMONIC EXAMPLE: "load ship usual decade human subway pen orbit midnight flag lend surround suit annual canal"','red'))
        exit(-1)

    """
    Collego tutti i vari contratti di cui è già stato fatto il deploy per l'interazione
    """
    
    print('Retrieving token contracts, please wait...')

    names=['Matteo','Diana','Francesco','Riccardo','Cristiano']

    Paycoin=Contract.from_abi("Paycoin",AddressesData['bot_minter']['paycoin'],Token.abi)
    tokens=[Contract.from_abi("Tokens",AddressesData[f'{name}']['token'], Token.abi) for name in names]
    pools=[Contract.from_abi("Tokens",AddressesData[f'{name}']['pool'], Pool.abi) for name in names]
    token_names=[AddressesData[f'{name}']['token name'] for name in names]
    token_symbols=[AddressesData[f'{name}']['token symbol'] for name in names]

    for name in names:
        if personal.address==AddressesData[name]['id']:
            personal_pool_id=AddressesData[name]['pool']
            personal_token_id=AddressesData[name]['token']
            personal_token_name=AddressesData[name]['token name']
            personal_token_symbol=AddressesData[name]['token symbol']

    personal_pool=Contract.from_abi('Pool',personal_pool_id,Pool.abi)
    personal_token=Contract.from_abi('Token',personal_token_id,Token.abi)

    """
    Varie stringhe utili nella UI del programma
    """

    option_list=['BUY','SELL','SWAP','INCREASE','DECREASE']
 
    op_type_asking='Please enter the operation you want to carry out '
    token1_asking_swap='Please enter the token name you want to trade in the SWAP '
    token2_asking_swap='Please enter the token name you want to acquire in the SWAP '
    token_to_buy= 'Please enter the token name you want to buy '
    token_to_sell= 'Please enter the token name you want to sell '

    """
    Printo il balance in Paycoin
    """

    print ('This is your balance: ', ether(Paycoin.balanceOf(personal)),' PcN')

    """
    Faccio andare il programma all'infinito
    """

    while True:

        print('\n\n')
        op_type=operation_type(op_type_asking,option_list)
        while not op_type in option_list:
            print('\nPlease enter a valid input, try to write it in CAPITAL LETTERS')
            op_type=operation_type(op_type_asking,option_list)
            

        print(f'Perfect, we are going to {op_type} something here.\n')

        if op_type=='SWAP':

            token_1=operation_type(token1_asking_swap,token_names)
            token_2=operation_type(token2_asking_swap,token_names)
            bool1= token_1 in token_names
            bool2= token_2 in token_names
            same= (token_1 == token_2)


            while (not bool1) or (not bool2) or same:      

                print(colored('\nplease enter token names among the existing ones (AND DIFFERENT ONES!)','red'))

                token_1=operation_type(token1_asking_swap,token_names)
                token_2=operation_type(token2_asking_swap,token_names)
                bool1= token_1 in token_names
                bool2= token_2 in token_names
                same=same= (token_1 == token_2)

            checkedbalance=False

            while not checkedbalance:
                    
                yourtoken1balance=ether(tokens[token_names.index(token_1)].balanceOf(personal))
                print(f'Ok, we are going to swap {token_1} with {token_2}')
                print(f'Your current balance of {token_1} is: ', yourtoken1balance,f'{token_symbols[token_names.index(token_1)]}')
                amount_2,typebool=check_input_type(f'Please enter the amount of {token_2} you want to acquire '+colored('WITHOUT *10**18 NOTATION, IT WILL BE  ADDED AUTOMATICALLY: ','red'), float)
                while not typebool:
                    print('Please enter an FLOAT amount', colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'))
                    amount_2,typebool=check_input_type(f'Please enter the amount of {token_2} you want to acquire: ', float)
                amount_2=float(amount_2)
                amount_1_needed=ether(pools[token_names.index(token_1)].get_swap_price(pools[token_names.index(token_2)], amount_2*10**18))
                checkedbalance=yourtoken1balance>=amount_1_needed
                
                if not checkedbalance:
                    print(colored(f'Your {token_1} balance is not sufficient to carry out the operation!','red'))
                    print('ahahahaha',ether(pools[token_names.index(token_1)].get_swap_price(pools[token_names.index(token_2)], amount_2*10**18)))
                    print(f'account {token_1} balance: ',yourtoken1balance,token_symbols[token_names.index(token_1)],' you need instead ',ether(pools[token_names.index(token_1)].get_swap_price(pools[token_names.index(token_2)], amount_2*10**18)),f' {token_symbols[token_names.index(token_1)]}!')
                    print('EXITING THE PROGRAM')
                    exit(-1)
                
            print(f'SWAPPING {amount_2} {token_symbols[token_names.index(token_2)]} for {amount_1_needed} {token_symbols[token_names.index(token_1)]}')
            gas_price=get_gas_price()
            t=threading.Thread(target=swap, args=(pools[token_names.index(token_1)],pools[token_names.index(token_2)],tokens[token_names.index(token_1)],amount_2*10**18,personal,gas_price))

        elif op_type=='BUY':

            token_to_buy=operation_type(token_to_buy,token_names)     
            bool= token_to_buy in token_names
            while not bool :         

                print(colored('Please enter a token name among the existing ones: ','red'))

                token_to_buy=operation_type(token_to_buy,token_names)     
                bool= token_to_buy in token_names

            checkedbalance=False
            while not checkedbalance:
                    
                your_pcn_balance=ether(Paycoin.balanceOf(personal))
                print(f'Ok, we are going to buy {token_to_buy} using your paycoin')
                print('Your current Paycoin balance is: ', your_pcn_balance,' PcN')
                amount,typebool=check_input_type(f'Please enter the amount of {token_to_buy} you want to buy'+colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'), float)
                while not typebool:
                    print('Please enter a float amount!')
                    amount,typebool=check_input_type(f'Please enter the amount of {token_to_buy} you want to buy'+colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'), float)

                amount=float(amount)
                amount_in_pcn=ether(pools[token_names.index(token_to_buy)].Get_Token_Price(amount*10**18))
                checkedbalance=your_pcn_balance>=amount_in_pcn
                    
                if not checkedbalance:
                    print(colored(f'Your Paycoin balance is not enough to buy {amount} {token_symbols[token_names.index(token_to_buy)]}, {amount_in_pcn} PcN are required!','red'))
                    print(colored(f'account Paycoin balance: {your_pcn_balance} PcN','red'))
                
                print(f'BUYING {amount} {token_symbols[token_names.index(token_to_buy)]} using {amount_in_pcn} PcN')
                gas_price=get_gas_price()
                t=threading.Thread(target=buy, args=(Paycoin,pools[token_names.index(token_to_buy)],amount*10**18,personal,gas_price))

        elif op_type=='INCREASE':

            checkedbalance=False
            while not checkedbalance:
                    
                your_pcn_balance=ether(Paycoin.balanceOf(personal))
                your_token_balance=ether(personal_token.balanceOf(personal))
                print('Your current Paycoin balance is: ', your_pcn_balance,' PcN')
                print('Your current token balance is: ', your_token_balance,f' {personal_token_symbol}')

                amount,typebool=check_input_type(f'Please enter the amount of {personal_token_name} you want to put in the pool to increase liquidity '+colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'), float)
                while not typebool:
                    print('Please enter a float amount!')
                    amount,typebool=check_input_type(f'Please enter the amount of {personal_token_name} you want to put in the pool to increase liquidity '+colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'), float)

                amount=float(amount)
                paycoin_ToAdd = personal_pool.paycoins_needed_to_increase_Token(amount*10**18,{'from':personal})

                lets_get_real_amount=amount*1.05
                lets_get_real_paycoin=paycoin_ToAdd*1.05

                print('\nYou are going to pay', ether(paycoin_ToAdd), f'PcN to increase liquidity with {amount} {personal_token_symbol}')
                print('Checking your balances...')

                bool1=lets_get_real_amount>=ether(personal_token.balanceOf(personal))
                bool2=lets_get_real_paycoin>=ether(Paycoin.balanceOf(personal))

                checkedbalance= bool1 and bool2
                
                if not checkedbalance:
                    print(colored(f'Maybe your Paycoin balance is not enough to increase liquidity, you have {your_pcn_balance} PcN, you need {lets_get_real_paycoin} PcN!','red'))
                    print(colored(f'Maybe your token balance is not enough, you have {your_tkn_balance} {personal_token_symbol}, you need {lets_get_real_amount} {personal_token_symbol}!'))
                    print('Terminating the program')
                    exit(-1)

                print(f'INCREASING LIQUIDITY, this could take a while...')
                thr=[]
                gas_price=get_gas_price()
                print('approving personal token')
                thr.append(threading.Thread(target=personal_token.approve, args=(personal_pool,amount*10**18*1.05,{'from': personal})))
                thr[-1].start()
                thr.append(threading.Thread(Paycoin.approve, args=(personal_pool,paycoin_ToAdd*1.05,{'from': personal})))
                thr[-1].start()
                for t in thr:
                    t.join()
                print('Increasing:')
                gas_price=get_gas_price()
                t=threading.Thread(target=personal_pool.increase_Token, args=(amount*10**18,{'from':personal}))

        elif op_type=='DECREASE':

            checkedbalance=False
            while not checkedbalance:
                    
                your_pool_balance=ether(personal_token.balanceOf(personal_pool))
                print('Your current Paycoin balance is: ', your_pcn_balance,' PcN')
                print('Your current token balance is: ', your_token_balance,f' {personal_token_symbol}')

                amount,typebool=check_input_type(f'Please enter the amount of {personal_token_name} you want to withdraw from the pool to decrease liquidity '+colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'), float)
                while not typebool:
                    print('Please enter a float amount!')
                    amount,typebool=check_input_type(f'Please enter the amount of {personal_token_name} you want to withdraw from the pool to decrease liquidity '+colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'), float)

                amount=float(amount)
                print('Checking your balances...')

                checkedbalance=amount>=ether(personal_token.balanceOf(personal_pool))
                
                if not checkedbalance:
                    print(colored(f'Pool\'s token balance is not enough, it has {your_pool_balance} {personal_token_symbol}, you wanted {amount} {personal_token_symbol}!'))
                    print('Terminating the program')
                    exit(-1)

                print(f'DECREASING LIQUIDITY, this could take a while...')
                gas_price=get_gas_price()
                t=threading.Thread(target=personal_pool.decrease_Token, args=(amount*10**18,{'from':personal}))

        else:

            token_to_sell=operation_type(token_to_sell,token_names)     
            bool= token_to_sell in token_names
            while not bool :         #else zio mi hai dato dei nomi sbagliati dei token

                print(colored('Please enter a token name among the existing ones: ','red'))

                token_to_sell=operation_type(token_to_sell,token_names)     
                bool= token_to_sell in token_names

            checkedbalance=False
            while not checkedbalance:
                    
                your_tkn_balance=ether(tokens[token_names.index(token_to_sell)].balanceOf(personal))
                print(f'Ok, we are going to sell {token_to_sell}')
                print(f'Your current {token_to_sell} balance is: ', your_tkn_balance,f' {token_symbols[token_names.index(token_to_sell)]}')
                amount,typebool=check_input_type(f'Please enter the amount of {token_to_sell} you want to sell'+colored ('(WITHOUT *10**18 NOTATION, IT WILL BE AUTOMATICALLY ADDED) ','red'), float)
                while not typebool:
                    print('Please enter an FLOAT amount',colored(' (WITHOUT *10**18 NOTATION, IT WILL BE AUTOMATICALLY ADDED): ','red'))
                    amount,typebool=check_input_type(f'Please enter the amount of {token_to_sell} you want to sell: ', float)

                amount=float(amount)
                checkedbalance=your_tkn_balance>=amount
                    
                if not checkedbalance:
                    print(colored(f'You do not posses enough {token_to_sell} to sell {amount} {token_symbols[token_names.index(token_to_sell)]}!','red'))
                    print(f'account {token_to_sell} balance: ', your_tkn_balance,token_symbols[token_names.index(token_to_sell)])
                    print('Closing the program')
                    exit(-1)
                
                amount_in_pcn=ether(pools[token_names.index(token_to_sell)].Get_Token_Price(amount*10**18))

                print(f'SELLING {amount} {token_symbols[token_names.index(token_to_sell)]} and receiving {amount_in_pcn} PcN')
                gas_price=get_gas_price()
                t=threading.Thread(target=sell,args=(pools[token_names.index(token_to_sell)],tokens[token_names.index(token_to_sell)],amount*10**18,personal,gas_price))
        
        print('Transaction sent, waiting for approval\n\n')
        t.start()
        t.join()
        print('=========TRANSACTION CARRYED OUT=========')
        print('\nNew user balance:\n ')
        print('Paycoin balance: ', ether(Paycoin.balanceOf(personal)),' PcN')
        for i in range(0,len(tokens)):
            print(f'{token_names[i]} balance: ', ether(tokens[i].balanceOf(personal)),f' {token_symbols[i]}')
        print('')
        print('=========================================')

        print('\nNew transaction starting...')
    


