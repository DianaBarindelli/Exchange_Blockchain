from inspect import signature
from brownie import *
from brownie.network.account import PublicKeyAccount, LocalAccount
from terminaltables import AsciiTable
from datetime import datetime
from hexbytes import HexBytes
import random
import json
import eth_abi
import subprocess

#funzione che interagisce con i log degli eventi nella blockchain
def get_logs(address, from_block, to_block, signature, topic1=None, topic2=None, topic3=None):
	return web3.eth.getLogs({
	'address': address,
	'fromBlock':from_block,
	'toBlock': to_block,
	'topics':[signature, topic1, topic2, topic3]
	})
	
#carico il progetto 'Name_project' che conterrà tutti i contracts, pyscripts ecc...
p=project.load('.', name='Name_project')
p.load_config()
from brownie.project.Name_project import *

#funzione printFile che mi servirà per printare ciò che voglio, in ingresso prende text=nome con cui printo il file; filename=nome del file.
def printFile(text, filename):
	with open(filename, 'a') as f:
		f.write(text+'\n')
		
#funzione che mi ripulisce il file 'filename' che contiene la quantità di paicoin, token, prezzo del token e data.
def clean(filename):
	with open(filename, 'w') as f:
		f.write('Paycoins\tTokens\tPrice\tDate\n')
		

#funzione time che mi restituisce il tempo (penso da quando sia partita la sfida)
def time(data):
	return(t.strftime('%Y-%m-%d %H:%M:%S', t.localtime(data)))
		

#funzione che prende in ingresso un indirizzo, e verifica se questo combacia con l'indirizzo di uno di noi o di un bot; in ogni caso printa la risposta		
def user_name(addr):
	for i in people:
		if people[i].lower() == addr.lower():
			return (i)
	return ('bots')
	
	
pool= './log.txt'  #file che contiene tutte le info delle transazioni della pool
pay_token_price = './log_paytokenprice.txt'  #file che contiene le quantità spostate di paycoin, token e il loro rapporto (price) per ogni evento
tokenbalances = './log_tokenbalances.txt'   #file che contiene le info sulle quantità di token dei player
paycoinbalances = './log_paycoinbalances.txt'  #file che contiene le info sulle quantità di paycoin dei player
feesf = './fees.txt'  #file che contiene le info sulle fees pagate dai player

#svuoto i due file relativi alla pool e ai token di pagamento
clean(pool)
clean(pay_token_price)  

with open(paycoinbalances, 'w') as f:
	f.write('Fra\tCri\tRichi\tMatte\tDiana\tDate\n')
	
with open(tokenbalances, 'w') as f:
	f.write('Fra\tCri\tRichi\tMatte\tDiana\tDate\n')

with open(feesf, 'w') as f:
	f.write('Fra\tCri\tRichi\tMatte\tDiana\tDate\n')
	

#carico il file json con tutti gli indirizzi: -Personali ; -Pool ; -Token ; -Challenge ; -Paycoin ; -Bots
Data = json.loads(open('addresses.json').read())


#Associo ad ogni utente il suo indirizzo
people={"Francesco":Data["Francesco"]["id"] ,"Cristiano":Data["Cristiano"]["id"] ,"Riccardo":Data["Riccardo"]["id"] ,
"Matteo":Data["Matteo"]["id"], 'Diana':Data['Diana']["id"]}

#inizialmente, prima dei vari mint, tutti avremo zero token
Init_tokenbalances = {'Francesco':0, 'Cristiano':0, 'Riccardo':0, 'Matteo':0, 'Diana':0, 'Bots':0}
#inizialmente, prima dei vari mint, tutti avremo zero paycoin
Init_paycoinbalances = {'Francesco':0, 'Cristiano':0, 'Riccardo':0, 'Matteo':0, 'Diana':0, 'Bots':0}
#inizialmente, prima delle varie operazioni, tutti avremo zero fee
#Init_feesbalances = {'Francesco':0, 'Cristiano':0, 'Riccardo':0, 'Matteo':0, 'Diana':0, 'Bots':0}

#connessione alla rete
network.connect('ropsten')

#collegamento al contratto sol della pool
contractAddress = #indirizzo della pool
contr_pool = Contract.from_abi('Pool', contractAddress, pool_abi.abi)


#filtro tutti gli eventi relativi al contractAddress (pool)
filt = web3.eth.filter({'address': contractAddress, 'fromBlock':0, 'toBlock':'latest'})
log = filt.get_all_entries()

#log dei vari eventi presenti nella pool
Bought_events = web3.keccak(text='Bought(address,address, uint256, uint256, uint256, uint256)').hex()
Sold_events = web3.keccak(text='Sold(address,address, uint256, uint256, uint256, uint256)').hex()
Swapp_events = web3.keccak(text='Swapp(address,address,address, uint256, uint256, uint256, uint256)').hex()
Increase_events = web3.keccak(text='Increase(address,address,uint256, uint256, uint256)').hex()
Decrease_events = web3.keccak(text='Decreaseaddress,address,uint256, uint256, uint256)').hex()


#ciclo di lettura dei log e stampa dei risultati:
if len(log) > 0:
	for i in log:  #ciclo su tutti i log presenti nel contractAddress(Pool)
		data_evento=''
		sign = '0x'+''.join(format(x, '02x') for x in i['topics'][0])  #crea l'hash del topic[0]; questo hash mi identifica l'evento (tipo bought)
		sender = '0x'+''.join(format(x, '02x') for x in i['topics'][1]) #crea l'hash del topich[1]; questo hash identifica l'indirizzo di chi ha effettuato l'evento
		data = i['data'] #quantità di token che vengono scambiati (acquistati nel caso dell'evento bought, venduti nel caso dell'evento sell)  NON SONO SICURO DI QUESTO
		
		if sign == Bought_events:  #se il topic[0] coincide con l'hash dell'evento bought
			print('--Bought--')
			printFile('--bought--', pool) #inserisco nel file pool che è stato effettuato un'acquisto
			data_decoded = eth_abi.decode_abi(['address','address', 'uint256','uint256', 'uint256', 'uint256'], HexBytes(data)) #mi decodifica il log nell'input dell'evento
			# BUY : 
			# address buyer:   indirizzo di chi compra
			# address this_pool:   indirizzo pool da cui vengono comprati i token
			# uint256 token_out:  token comprati, in uscita dalla pool
			# uint256 paycoin_in:    paycoin usati dal buyer, che entrano nella pool 
			# uint256 fees:       fees pagate dal buyer, che vanno al proprietario della pool
			# uint256 time
			
			
			data_evento = str(time(data_decoded[5])) # momento in cui uno attua l'evento buy 
			print('buyer:'+str(data_decoded[0]))
			print('pool:'+str(data_decoded[1]))
			print('tokenOut_amount:'+str(data_decoded[2]))
			print('paycoinIn_amount:'+str(data_decoded[3]))
			print('fees:'+str(data_decoded[4]))
			printFile('buyer:'+str(data_decoded[0]), pool) #oltre a printarlo su schermo, salvo anche sul file pool chi è il sender dell'evento
			printFile('pool:'+str(data_decoded[1],pool))
			printFile('tokenOut_amount:'+str(data_decoded[2]), pool) #e la quantità
			printFile('paycoinIn_amount:'+str(data_decoded[3]),pool)
			printFile('fees:'+str(data_decoded[4]),pool)
			printFile('time:'+data_evento, pool) #e quando è avvenuto
			
			pay_amount = data_decoded[3] #dovremmo inserire nell'evento bought (come input) anche quanti paycoin deve spendere  per avere i tkn_amount chi vuole comprare
			tkn_amount = data_decoded[2]  #non so se sono gia considerate le fee in questi input
			price = pay_amount / tkn_amount  #rapporto tra paycoin spesi e token acquisiti
			fees = data_decoded[4]
			buyer = data_decoded[0]
			printFile(str(pay_amount)+'\t'+str(tkn_amount)+'\t'+str(price)+'\t'+data_evento, pay_token_price)  #salvo l'info nel file
		 #salvo su file andamento fees

			name = user_name(str(data_decoded[0]))
			printFile(name + '\t' +str(fees)+'\t' +data_evento, feesf)
			token_balances[name] += data_decoded[2]
			paycoin_balances[name] -= data_decoded[3] 
			printFile(name + '\t' +str(token_balances[name])+'\t' +data_evento, tokenbalances)
			printFile(name + '\t' +str(paycoin_balances[name])+'\t' +data_evento, paycoinbalances)
			
		
		elif sign == Sold_events:  #se il topic[0] coincide con l'hash dell'evento bought
			print('--Sold--')
			printFile('--sold--', pool) #inserisco nel file pool che è stato effettuato un'acquisto
			data_decoded = eth_abi.decode_abi(['address','address', 'uint256','uint256', 'uint256', 'uint256'], HexBytes(data)) #mi decodifica il log nell'input dell'evento
			# SOLD : 
			# address seller:   indirizzo di chi vende
			# address this_pool:   indirizzo pool a cui vengono venduti i token
			# uint256 token_in:  token venduti, in entrata nella pool
			# uint256 paycoin_out:    paycoin ricavati dalla vendita, che entrano al seller
			# uint256 fees:   fees pagate dal seller, che vanno al proprietario della pool
			# uint256 time
			
			
			
			data_evento = str(time(data_decoded[5])) #se ci fosse come input il momento in cui uno attua l'evento buy per esempio
			print('seller:'+str(data_decoded[0]))
			print('pool:'+str(data_decoded[1]))
			print('tokenIn_amount:'+str(data_decoded[2]))
			print('paycoinOut_amount:'+str(data_decoded[3]))
			print('fees:'+str(data_decoded[4]))
			printFile('seller:'+str(data_decoded[0]), pool) #oltre a printarlo su schermo, salvo anche sul file pool chi è il sender dell'evento
			printFile('pool:'+str(data_decoded[1]),pool)
			printFile('tokenIn_amount:'+str(data_decoded[2]), pool) #e la quantità
			printFile('paycoinOut_amount:'+str(data_decoded[3]),pool)
			printFile('fees:'+str(data_decoded[4]),pool)
			printFile('time:'+data_evento, pool) #e quando è avvenuto
			
			pay_amount = data_decoded[3] #dovremmo inserire nell'evento bought (come input) anche quanti paycoin deve spendere  per avere i tkn_amount chi vuole comprare
			tkn_amount = data_decoded[2]  #non so se sono gia considerate le fee in questi input
			price = pay_amount / tkn_amount  #rapporto tra paycoin spesi e token acquisiti
			fees = data_decoded[4]
	
			printFile(str(pay_amount)+'\t'+str(tkn_amount)+'\t'+str(price)+'\t'+data_evento, pay_token_price)  #salvo l'info nel file
		

			name = user_name(str(data_decoded[0]))
			token_balances[name] -= data_decoded[2]
			paycoin_balances[name] += data_decoded[3]
			printFile(name + '\t' +str(fees)+'\t' +data_evento, feesf)
			printFile(name + '\t' +str(token_balances[name])+'\t' +data_evento, tokenbalances)
			printFile(name + '\t' +str(paycoin_balances[name])+'\t' +data_evento, paycoinbalances)

		elif sign == Swapp_events:  #se il topic[0] coincide con l'hash dell'evento bought
			print('--Swapp--')
			printFile('--swapp--', pool) #inserisco nel file pool che è stato effettuato un'acquisto
			data_decoded = eth_abi.decode_abi(['address','address','address', 'uint256','uint256', 'uint256', 'uint256'], HexBytes(data)) #mi decodifica il log nell'input dell'evento
			# SWAPP : 
			# address swapper:   indirizzo di chi fa lo swap
			# address this_pool:   indirizzo della poolA del tokenA da scambiare
			# uint256 poolB:  indirizzo della poolB del tokenB che voglio in cambio
			# uint256 token_out:    tokenA in uscita per lo scambio
			# uint256 token_in:   tokenB in entrata dopo lo scambio
			# uint256 fees:   fees pagate dal seller
			# uint256 time
			
			data_evento = str(time(data_decoded[6])) #se ci fosse come input il momento in cui uno attua l'evento buy per esempio
			print('swapper:'+str(data_decoded[0]))
			print('PoolA:'+str(data_decoded[1]))
			print('PoolB:'+str(data_decoded[2]))
			print('tokenAOut_amount:'+str(data_decoded[3]))
			print('tokenBIn_amount:'+str(data_decoded[4]))
			print('fees:'+str(data_decoded[5]))
			printFile('swapper:'+str(data_decoded[0]), pool) #oltre a printarlo su schermo, salvo anche sul file pool chi è il sender dell'evento
			printFile('PoolA:'+str(data_decoded[1]),pool)
			printFile('PoolB:'+str(data_decoded[2]),pool)
			printFile('tokenAOut_amount:'+str(data_decoded[3]),pool) #e la quantità
			printFile('tokenBIn_amount:'+str(data_decoded[4]),pool)
			printFile('fees:'+str(data_decoded[5]),pool)
			printFile('time:'+data_evento, pool) #e quando è avvenuto
			
			fees = data_decoded[5]
		
		
			name = user_name(str(data_decoded[0]))
			printFile(name + '\t' +str(fees)+'\t' +data_evento, feesf)
			token_balances[name] -= data_decoded[4]
			printFile(name + '\t' +str(token_balances[name])+'\t' +data_evento, tokenbalances)
			

		elif sign == Increase_events:  #se il topic[0] coincide con l'hash dell'evento bought
			print('--Increase--')
			printFile('--increase--', pool) #inserisco nel file pool che è stato effettuato un'acquisto
			data_decoded = eth_abi.decode_abi(['address','address','uint256','uint256','uint256'], HexBytes(data)) #mi decodifica il log nell'input dell'evento
			data_evento = str(time(data_decoded[4])) #se ci fosse come input il momento in cui uno attua l'evento buy per esempio
			print('increaser:'+str(data_decoded[0]))
			print('increaserPool:'+str(data_decoded[1]))
			print('Token_increase:'+str(data_decoded[2]))
			print('Paycoin_increase:'+str(data_decoded[3]))
			printFile('increaser:'+str(data_decoded[0],pool))
			printFile('increaserPool:'+str(data_decoded[1]),pool)
			printFile('Token_increase:'+str(data_decoded[2]),pool)
			printFile('Paycoin_increase:'+str(data_decoded[3]),pool) #oltre a printarlo su schermo, salvo anche sul file pool chi è il sender dell'evento
			printFile('time:'+data_evento, pool) #e quando è avvenuto
			
			name = user_name(str(data_decoded[0]))
			token_balances[name] -= data_decoded[2]
			paycoin_balances[name] -= data_decoded[3]

			printFile(name + '\t' +str(token_balances[name])+'\t' +data_evento, tokenbalances)
			printFile(name + '\t' +str(paycoin_balances[name])+'\t' +data_evento, paycoinbalances)

		elif sign == Decrease_events:  #se il topic[0] coincide con l'hash dell'evento bought
			print('--Decrease--')
			printFile('--decrease--', pool) #inserisco nel file pool che è stato effettuato un'acquisto
			data_decoded = eth_abi.decode_abi(['address','address','uint256','uint256','uint256'], HexBytes(data)) #mi decodifica il log nell'input dell'evento
			data_evento = str(time(data_decoded[4])) #se ci fosse come input il momento in cui uno attua l'evento buy per esempio
			print('decreaser:'+str(data_decoded[0]))
			print('decreaserPool:'+str(data_decoded[1]))
			print('Token_decrease:'+str(data_decoded[2]))
			print('Paycoin_decrease:'+str(data_decoded[3]))
			printFile('decreaser:'+str(data_decoded[0]),pool)
			printFile('decreaserPool:'+str(data_decoded[1]),pool)
			printFile('Token_decrease:'+str(data_decoded[2]),pool)
			printFile('Paycoin_decrease:'+str(data_decoded[3]),pool) #oltre a printarlo su schermo, salvo anche sul file pool chi è il sender dell'evento
			printFile('time:'+data_evento, pool) #e quando è avvenuto
			
			name = user_name(str(data_decoded[0]))
			token_balances[name] += data_decoded[2]
			paycoin_balances[name] += data_decoded[3]

			printFile(name + '\t' +str(token_balances[name])+'\t' +data_evento, tokenbalances)
			printFile(name + '\t' +str(paycoin_balances[name])+'\t' +data_evento, paycoinbalances)
			






		#printFile(str(token_balances['Fra'] +'\t'+ str(token_balances['Cri'] +'\t'+ str(token_balances['Richi'] +'\t'+ str(token_balances['Matte'] +'\t'+ str(token_balances['Diana'] +'\t'+ data_evento, tokenbalances)  #salvo le info sul foglio tokenbalances
		#printFile(str(paycoin_balances['Fra'] +'\t'+ str(paycoin_balances['Cri'] +'\t'+ str(paycoin_balances['Richi'] +'\t'+ str(paycoin_balances['Matte'] +'\t'+ str(paycoin_balances['Diana'] +'\t'+ data_evento, paycoinbalances)
		#printFile(str(fees_balances['Fra'] +'\t'+ str(fees_balances['Cri'] +'\t'+ str(fees_balances['Richi'] +'\t'+ str(fees_balances['Matte'] +'\t'+ str(fees_balances['Diana'] +'\t'+ data_evento, feesbalances)
		



























