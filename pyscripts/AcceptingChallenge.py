# REQUIREMENTS: SCHEDULE LIBRARY
import time
import os 

from brownie import *
import json
from brownie import Contract
from web3 import Web3
from brownie.network.gas.strategies import GasNowStrategy
import sys
import schedule

network.connect('ropsten')
#network.connect('development')

PrivateData=json.loads(open('private_dict.json').read())
myAccount=accounts.from_mnemonic(PrivateData['personal_account']['mnemonic'], count=1)

##############################

c = open('challenge.json')
dataChallenge = json.load(c)
c.close()

#################################

challenge = Contract.from_abi(dataChallenge['name'], dataChallenge['address'], dataChallenge['abi'])

def readLog():
    print("I'm reading the logs...")

schedule.every(10).seconds.do(readLog)

while True:
    schedule.run_pending()
    
    if("trovo il mio nome nella challenge, leggeendo dai logs tipo se trovo"):
        TimeLeft = challenge.timeLeft({'from' : myAccount}) 
        if TimeLeft > 0 :        
            time.sleep(TimeLeft)
            os.system("python ChallengeManager.py accept")
    time.sleep(1)

