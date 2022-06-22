from brownie.network import accounts
from brownie import web3, network, project, Contract

from hexbytes import HexBytes
import eth_abi
import codecs
import time as t, datetime


#carico il progetto 'Name_project' che conterrà tutti i contracts, pyscripts ecc...
p=project.load('.', name='ProjectName')
p.load_config()
from brownie.project.UniMiSwap import *

#funzione che interagisce con i log degli eventi nella blockchain
def get_logs(address, from_block, to_block, signature, topic1=None, topic2=None, topic3=None):
	return web3.eth.getLogs({
		"address": address,
		"fromBlock": from_block,
		"toBlock": to_block,
		"topics": [signature, topic1, topic2, topic3]
		})

#funzione per printare su file 'log_challenge.txt'		
def printFile(text):
	with open("./log_challenge.txt","a") as f:
		f.write(str(text)+'\n')

		
nets = ["ropsten","development"]
net = nets[0]
network.connect(net)

if network.is_connected():
	print("Connesso a "+net)
else :
	print("Errore di connessione a "+net)

#carico il file json con tutti gli indirizzi: -Personali ; -Pool ; -Token ; -Challenge ; -Paycoin ; -Bots
Data = json.loads(open('indirizzi.json').read())
contract_addr = Data["Challenge"]
contr = Contract.from_abi("Challenge", contract_addr, Challenge.abi)



#filtro tutti gli eventi relativi al contractAddress (Challenge)
filt = web3.eth.filter({"address": contract_addr, "fromBlock": 0, "toBlock":'latest'})
logs = filt.get_all_entries()

#log dei vari eventi presenti nella Challenge
event1vs1=web3.keccak(text="Challenge1v1Launched(uint256,address,address,uint256)").hex()
event1vs2=web3.keccak(text="Challenge1v2Launched(uint256,address,address,address,uint256)").hex()
eventEnd=web3.keccak(text="ChallengeEnded(uint256,address,uint256)").hex()


#print(logs)


if len(logs) > 0:
	for i in logs:
		#print(i['data'],'\n')

		sign = "0x"+"".join(format(x, '02x') for x in i['topics'][0])
		data = i['data']
		
		if sign == event1vs1:
			print("-- Challenge 1v1 Launched --")
			printFile("-- Challenge 1v1 Launched  --")
			data_decoded = eth_abi.decode_abi(['uint256','address','address','uint256'], HexBytes(data))
			event_date = str(t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(data_decoded[3])))
            
            		print(data_decoded[0]) #challenge number
			print("Launcher:",data_decoded[1])
			print("Target:",data_decoded[2])
            		print("Time: "+event_date)
			#print(time.strftime("%Z - %Y/%m/%d, %H:%M:%S", str(time.localtime(data_decoded[3]))))
			printFile(data_decoded[0]) #challenge number
			printFile("Launcher: "+data_decoded[1])
			printFile("Target: "+data_decoded[2])
            		printFile("Time: "+event_date)
			#printFile(time.strftime("%Z - %Y/%m/%d, %H:%M:%S"+str(time.localtime(data_decoded[3]))))
			
		elif sign == event1vs2:
			print("-- Challenge 1v2 Launched --")
			printFile("-- Challenge 1vs Launched --")
			data_decoded = eth_abi.decode_abi(['uint256','address','address','address','uint256'], HexBytes(data))
			
			event_date = str(t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(data_decoded[4])))
			
			print(data_decoded[0]) #challenge number
			print("Launcher:",data_decoded[1])
			print("Target1:",data_decoded[2])
            		print("Time: "+event_date)
            		print("Target2:",data_decoded[3])
            		print("Time: "+event_date)
			printFile(data_decoded[0]) #challenge number
			printFile("Launcher:",data_decoded[1])
			printFile("Target1:",data_decoded[2])
            		printFile("Time: "+event_date)
            		printFile("Target2:",data_decoded[3])
            		printFile("Time: "+event_date)
			
		elif sign == eventEnd:		
			print("-- Challenge Closed --")
			printFile("-- Challenge Closed --")
			data_decoded = eth_abi.decode_abi(['uint256','address','uint256'], HexBytes(data))
			
			event_date = str(t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(data_decoded[2])))
			
			print(data_decoded[0]) #challenge number
			print("Winner:",data_decoded[1])
			print("Time: "+event_date)
			printFile(data_decoded[0]) #challenge number
			printFile("Winner: "+data_decoded[1])
			printFile("Time: "+event_date)
			
	
    printFile("---END UPDATE "+str(datetime.datetime.now())+"_ _")

