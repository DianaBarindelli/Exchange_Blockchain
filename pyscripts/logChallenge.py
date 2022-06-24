from brownie.network import accounts
from brownie import web3, network, project, Contract

from hexbytes import HexBytes
import eth_abi
import codecs
import time as t, datetime
import json
import schedule

Players = { '0xc89304be60b1184281cdacf8e9add215b960fcb8': 'Pacho',
            '0xebf84b5aa7a66412863f8f66655b5876ef92d91f': 'Citte', 
            '0x66f26b71404a133f4e478fb5f52a8105fb324f6e': 'Fra',
            '0x4f6374606526bc5892d5c3037ce68da5712B4efe': 'Becca',
            '0x0b3de044dc8b2902e6B668cc43bfedb39dfa8fcd': 'Diana'}

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

def printFileOV(text):
	with open("./log_challenge.txt","w") as f:
		f.write(str(text)+'\n')

def job():
	#carico il progetto 'Name_project' che conterrà tutti i contracts, pyscripts ecc...
	p = project.load('/home/cristiano/blockchain_test/challenge', name = "TokenProject")
	p.load_config()
	from brownie.project.TokenProject import Challenge


	nets = ["ropsten","development"]
	net = nets[0]
	network.connect(net)

	if network.is_connected():
		print("Connesso a "+net)
	else :
		print("Errore di connessione a " + net)

	#carico il file json con tutti gli indirizzi: -Personali ; -Pool ; -Token ; -Challenge ; -Paycoin ; -Bots
	#Data = json.loads(open('indirizzi.json').read())
	#contract_addr = Data["Challenge"]
	contract_addr = '0x3D2aD3DF24cE150E3a5a1F2122a660dDB0Eeaf67'
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
		printFileOV("-- STARTING --")
		for i in logs:
			#print(i['data'],'\n')
			sign = "0x"+"".join(format(x, '02x') for x in i['topics'][0])
			data = i['data']	
			if sign == event1vs1:
				print("-- Challenge 1v1 Launched --")
				printFile("-- Challenge 1v1 Launched --")
				data_decoded = eth_abi.decode_abi(['uint256','address','address','uint256'], HexBytes(data))
				event_date = str(t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(data_decoded[3])))
				print("Challenge number: ",data_decoded[0]) 
				print("Launcher: ",Players[data_decoded[1]])
				print("Target: ",Players[data_decoded[2]])
				print("Time: "+event_date)
				#print(time.strftime("%Z - %Y/%m/%d, %H:%M:%S", str(time.localtime(data_decoded[3]))))
				printFile("Challenge number:"+str(data_decoded[0])) 
				printFile("Launcher: "+Players[data_decoded[1]])
				printFile("Target: "+Players[data_decoded[2]])
				printFile("Time: "+event_date)
				#printFile(time.strftime("%Z - %Y/%m/%d, %H:%M:%S"+str(time.localtime(data_decoded[3]))))
				
			elif sign == event1vs2:
				print("-- Challenge 1v2 Launched --")
				printFile("-- Challenge 1vs2 Launched --")
				data_decoded = eth_abi.decode_abi(['uint256','address','address','address','uint256'], HexBytes(data))
				
				event_date = str(t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(data_decoded[4])))
				
				print("Challenge number: ",data_decoded[0]) 
				print("Launcher:",Players[data_decoded[1]])
				print("Target1:",Players[data_decoded[2]])
				print("Time: "+event_date)
				print("Target2:",Players[data_decoded[3]])
				print("Time: "+event_date)
				printFile("Challenge number:"+str(data_decoded[0])) 
				printFile("Launcher:"+Players[data_decoded[1]])
				printFile("Target1:"+Players[data_decoded[2]])
				printFile("Time: "+event_date)
				printFile("Target2:"+Players[data_decoded[3]])
				printFile("Time: "+event_date)
				
			elif sign == eventEnd:		
				print("-- Challenge Closed --")
				printFile("-- Challenge Closed --")
				data_decoded = eth_abi.decode_abi(['uint256','address','uint256','string'], HexBytes(data))
				
				event_date = str(t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(data_decoded[2])))
				
				print("Challenge number:", data_decoded[0]) 
				print("Winner:",Players[data_decoded[1]])
				print("Time: "+event_date)
				print("Which challenge" + data_decoded[3])
				printFile("Challenge number: "+str(data_decoded[0])) 
				printFile("Winner: "+Players[data_decoded[1]])
				printFile("Time: "+event_date)
				printFile("Which challenge" + data_decoded[3])
				
		
		printFile("---END UPDATE "+str(datetime.datetime.now())+"_ _")

schedule.every(4).seconds.do(job)

while True:
    schedule.run_pending()
    t.sleep(1)
