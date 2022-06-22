from brownie import *
import json
from brownie import Contract
from web3 import Web3
from brownie.network.gas.strategies import GasNowStrategy
import sys

'''
    Usage (from command line):

    *** LAUNCH 1 VS 1 CHALLENGE ***
    $ python ChallengeManager.py launch_1v1 target1

    *** LAUNCH 1 VS 2 CHALLENGE ***
    $ python ChallengeManager.py launch_1v2 target1 target2
    
    *** ACCEPT CHALLENGE ***    
    $ python ChallengeManager.py accept 
'''

p = project.load('/home/cristiano/cartella_test', name = "TokenProject")

p.load_config()

from brownie.project.TokenProject import TokenZ, Challenge

Players = { 'Pacho': '0xc89304bE60b1184281cDacF8e9ADD215B960Fcb8',
            'Citte': '0xebf84b5aa7a66412863F8F66655B5876EF92d91F', 
            'Fra'  : '0x66F26b71404A133F4e478Fb5f52a8105fB324F6e',
            'Becca': '0x4f6374606526BC5892D5C3037cE68da5712B4Efe',
            'Diana': '0x0B3DE044dC8b2902e6B668Cc43bfedB39dfA8fcD'}


#alternativamente facciamo un load da un json, la sintassi sara comunque la stessa di qui sopra, tipo:
#f = open('NomeFile.json')
#Players = json.load(f)
#f.close()

network.connect('ropsten')
#network.connect('development')

print('connesso a ropsten')

PrivateData=json.loads(open('/home/cristiano/cartella_test/scripts/private_dict.json').read())
myAccount=accounts.from_mnemonic(PrivateData['personal_account']['mnemonic'], count=1)

print('caricato account personale di utente')

challenge_address = '0x3D2aD3DF24cE150E3a5a1F2122a660dDB0Eeaf67'
paytoken_address = '0x83f4d10487dD65E25FD2de52149921aCaF647c05'

challenge = Contract.from_abi('Challenge', challenge_address, Challenge.abi)
paytoken = Contract.from_abi('Paytoken', paytoken_address, TokenZ.abi)

print ('caricati indirizzi di challenge e paytoken')

if (len(sys.argv) == 3 and sys.argv[1] == 'launch_1v1'):
    print("++++++++++ LAUNCHING 1 VS 1 CHALLENGE +++++++++++")    
    target1 = Players[sys.argv[2]]
    challenge.launch_1v1(target1, {'from':myAccount})


if (len(sys.argv) == 4 and sys.argv[1] == 'launch_1v2'):
    print("++++++++++ LAUNCHING 1 VS 2 CHALLENGE +++++++++++")    
    target1 = Players[sys.argv[2]]
    target2 = Players[sys.argv[3]]
    challenge.launch_1v2(target1, target2, {'from':myAccount})


if (len(sys.argv) == 2 and sys.argv[1] == 'accept'):
    print("++++++++++ ACCEPTING +++++++++++")    
    challenge.accept({'from':myAccount})

if (len(sys.argv) == 1 and sys.argv[1] == 'forcedClosure'):
    print("++++++++++ forcing closure +++++++++++")    
    challenge.forcedClosure({'from':myAccount})

if (len(sys.argv) == 1 and sys.argv[1] == 'timeLeft'):
    print("++++++++++ checking time left +++++++++++")    
    challenge.timeLeft({'from':myAccount})

if (len(sys.argv) == 2 and sys.argv[1] == 'timeLeft'):
    print("++++++++++ remaining 1v1: +++++++++++")    
    challenge.left1v1(Players[sys.argv[2]], {'from':myAccount})

if (len(sys.argv) == 2 and sys.argv[1] == 'timeLeft'):
    print("++++++++++ remaining 1v2: +++++++++++")    
    challenge.left1v2(Players[sys.argv[2]], {'from':myAccount})


