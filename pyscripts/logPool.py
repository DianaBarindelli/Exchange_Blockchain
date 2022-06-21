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
	
	
pool= './logs/log.txt'  #file che contiene tutte le info delle transazioni della pool
pay_token_price = './logs/log_paytokenprice.txt'  #file che contiene le quantità spostate di paycoin, token e il loro rapporto (price) per ogni evento
tokenbalances = './logs/log_tokenbalances.txt'   #file che contiene le info sulle quantità di token dei player
paycoinbalances = './logs/log_paycoinbalances.txt'  #file che contiene le info sulle quantità di paycoin dei player


#svuoto i due file relativi alla pool e ai token di pagamento
clean(pool)
clean(pay_token_price)  

with open(paycoinbalances, 'w') as f:
	f.write('Fra\tCri\tRichi\tMatte\tDiana\tDate\n')
	
with open(tokenbalances, 'w') as f:
	f.write('Fra\tCri\tRichi\tMatte\tDiana\tDate\n')
	

#carico il file json con tutti gli indirizzi: -Personali ; -Pool ; -Token ; -Challenge ; -Paycoin ; -Bots
Data = json.loads(open('indirizzi.json').read())


#Associo ad ogni utente il suo indirizzo
people={"Francesco":Data["Fra"] ,"Cristiano":Data["Cri"] ,"Riccardo":Data["Richi"] ,
"Matteo":Data["Matte"], 'Diana':Data['Diana']}

#inizialmente, prima dei vari mint, tutti avremo zero token
Init_tokenbalances = {'Francesco':0, 'Cristiano':0, 'Riccardo':0, 'Matteo':0, 'Diana':0, 'Bots':0}
#inizialmente, prima dei vari mint, tutti avremo zero paycoin
Init_paycoinbalances = {'Francesco':0, 'Cristiano':0, 'Riccardo':0, 'Matteo':0, 'Diana':0, 'Bots':0}

#connessione alla rete
network.connect('ropsten')

#collegamento al contratto sol della pool
contractAddress = #indirizzo della pool
contr_pool = Contract.from_abi('Pool', contractAddress, pool_abi.abi)


#filtro tutti gli eventi relativi al contractAddress (pool)
filt = web3.eth.filter({'address': contractAddress, 'fromBlock':0, 'toBlock':'latest'})
log = filt.get_all_entries()

#log dei vari eventi presenti nella pool
Bought_events = web3.keccak(text='Bought(address, uint256)').hex()
ECCETERAAAAAA


#ciclo di lettura dei log e stampa dei risultati:
if len(log) > 0:
	for i in log:  #ciclo su tutti i log presenti nel contractAddress(Pool)
		data_evento=''
		sign = '0x'.''.join(format(x, '02x') for x in i['topics'][0])  #crea l'hash del topic[0]; questo hash mi identifica l'evento (tipo bought)
		sender = '0x'.''.join(format(x, '02x') for x in i['topics'][1]) #crea l'hash del topich[1]; questo hash identifica l'indirizzo di chi ha effettuato l'evento
		data = i['data'] #quantità di token che vengono scambiati (acquistati nel caso dell'evento bought, venduti nel caso dell'evento sell)  NON SONO SICURO DI QUESTO
		
		if sign == Bought_events:  #se il topic[0] coincide con l'hash dell'evento bought
			print('--Buy--')
			printFile('--buy--', pool) #inserisco nel file pool che è stato effettuato un'acquisto
			data_decoded = eth_abi.decode_abi(['address', 'uint256'], HexBytes(data)) #mi decodifica il log nell'input dell'evento
			#data_evento = str(time(data_decoded[#]) se ci fosse come input il momento in cui uno attua l'evento buy per esempio
			print('sender:'+str(data_decoded[0]))
			print('tkn_amount:'+str(data_decoded[1]))
			printFile('sender:'+str(data_decoded[0]), pool) #oltre a printarlo su schermo, salvo anche sul file pool chi è il sender dell'evento
			printFile('tkn_amount:'+str(data_decoded[1]), pool) #e la quantità
			printFile('time:'+data_evento, pool) #e quando è avvenuto
			
			pay_amount = data_decoded[#] #dovremmo inserire nell'evento bought (come input) anche quanti paycoin deve spendere  per avere i tkn_amount chi vuole comprare
			tkn_amount = data_decoded[1]  #non so se sono gia considerate le fee in questi input
			price = pay_amount / tkn_amount  #rapporto tra paycoin spesi e token acquisiti
			printFile(str(pay_amount)+'\t'+str(tkn_amount)+'t'+str(price)+'t'+data_evento, pay_token_price)  #salvo l'info nel file
			
			name = user_name(str(data_decoded[0])
			token_balances[name] += data_decoded[1]
			paycoin_balances[name] -= data_decoded[#]
			
			printFile(str(token_balances['Fra'] +'\t'+ str(token_balances['Cri'] +'\t'+ str(token_balances['Richi'] +'\t'+ str(token_balances['Matte'] +'\t'+ str(token_balances['Diana'] +'\t'+ data_evento, tokenbalances)  #salvo le info sul foglio tokenbalances
			printFile(str(paycoin_balances['Fra'] +'\t'+ str(paycoin_balances['Cri'] +'\t'+ str(paycoin_balances['Richi'] +'\t'+ str(paycoin_balances['Matte'] +'\t'+ str(paycoin_balances['Diana'] +'\t'+ data_evento, paycoinbalances)
		
		



























