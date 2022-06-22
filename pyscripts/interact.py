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
        temp_string+='{'+f'{option_list[i]}'+'}'
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

    """
    Varie stringhe utili nella UI del programma
    """

    option_list=['BUY','SELL','SWAP']
 
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
                print('Your current balance of token 1 is: ', yourtoken1balance,f'{token_symbols[token_names.index(token_1)]}')
                amount_1,typebool=check_input_type(f'Please enter the amount of {token_1} you want to trade '+colored('WITHOUT *10**18 NOTATION, IT WILL BE  ADDED AUTOMATICALLY: ','red'), int)
                while not typebool:
                    print('Please enter an FLOAT amount', colored(' (WITHOUT *10**18 NOTATION, IT WILL BE ADDED AUTOMATICALLY): ','red'))
                    amount_1,typebool=check_input_type(f'Please enter the amount of {token_1} you want to trade: ', float)
                amount_1=float(amount_1)
                checkedbalance=yourtoken1balance>=amount_1
                    
                if not checkedbalance:
                    print(colored(f'Your {token_1} balance is not sufficient to carry out the operation!','red'))
                    print(f'account {token_1} balance: ',token_symbols[token_names.index(token_1)])
                    print('EXITING THE PROGRAM')
                    exit(-1)
                
            amount_of_token_2=ether(pools[token_names.index(token_2)].How_Many_Token(pools[token_names.index(token_1)].Get_Token_Price(amount_1*10**18)))  #il numero dei token 2 che si riesce a comprare è calcolato sul valore in paycoin del token 1
            print(f'SWAPPING {amount_1} {token_symbols[token_names.index(token_1)]} for {amount_of_token_2} {token_symbols[token_names.index(token_2)]}')
            gas_price=get_gas_price()
            t=threading.Thread(target=swap, args=(pools[token_names.index(token_1)],pools[token_names.index(token_2)],tokens[token_names.index(token_1)],amount_1*10**18,personal,gas_price))

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
                    print('Please enter an INT amount!')
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
                amount,typebool=check_input_type(f'Please enter the amount of {token_to_sell} you want to sell'+colored (('(WITHOUT *10**18 NOTATION, IT WILL BE AUTOMATICALLY ADDED)','red')), float)
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
    


