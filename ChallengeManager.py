from brownie import *
import json
from brownie import Contract
from web3 import Web3
from brownie.network.gas.strategies import GasNowStrategy
import sys

Players = { 'Pacho': '0xc89304bE60b1184281cDacF8e9ADD215B960Fcb8',
            'Citte': '0xebf84b5aa7a66412863F8F66655B5876EF92d91F', 
            'Fra': '',
            'Becca': '',
            'Diana': '0x0B3DE044dC8b2902e6B668Cc43bfedB39dfA8fcD'}

#alternativamente facciamo un load da un json, la sintassi sara comunque la stessa di qui sopra

#network.connect('ropsten')
network.connect('development')

accounts.load("ACCOUNT_NAME")

##############################

c = open('challenge.json')
dataChallenge = json.load(c)
c.close()

###############################

p = open('paycoin.json')
dataPaycoin = json.load(p)
p.close()

#################################

challenge = Contract.from_abi(dataChallenge['name'], dataChallenge['address'], dataChallenge['abi'])
paytoken = Contract.from_abi(dataPaycoin['name'], dataPaycoin['address'], dataPaycoin['abi'])

if (len(sys.argv) == 3):
    print("++++++++++ LAUNCHING 1 VS 1 CHALLENGE +++++++++++")    
    target1 = Players[sys.argv[2]]
    challenge.launch_1v1(target1, {'from':accounts[0]})


if (len(sys.argv) == 4):
    print("++++++++++ LAUNCHING 1 VS 2 CHALLENGE +++++++++++")    
    target1 = Players[sys.argv[2]]
    target2 = Players[sys.argv[3]]
    challenge.launch_1v2(target1, target2, {'from':accounts[0]})


if (len(sys.argv) == 2):
    print("++++++++++ ACCEPTING +++++++++++")    
    challenge.accept({'from':accounts[0]})


