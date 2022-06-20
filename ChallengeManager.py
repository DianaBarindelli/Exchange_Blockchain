from brownie import *
import json
from brownie import Contract
from web3 import Web3
from brownie.network.gas.strategies import GasNowStrategy
import sys

'''
    Usage (from command line):

    *** LAUNCH 1 VS 1 CHALLENGE ***
    $ python ChallengeManager.py launch_1v1 target2

    *** LAUNCH 1 VS 2 CHALLENGE ***
    $ python ChallengeManager.py launch_1v2 target1 target2
    
    *** ACCEPT CHALLENGE ***    
    $ python ChallengeManager.py accept 
'''

Players = { 'Pacho': '',
            'Citte': '', 
            'Fra': '',
            'Becca': '',
            'Diana': ''}

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


