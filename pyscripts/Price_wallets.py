from brownie import *
import json
from datetime import date
from brownie import web3
import time
from datetime import datetime

AddressesData=json.loads(open('addresses.json').read())

p=project.load('../',name='firstproject')
p.load_config()
from brownie.project.firstproject import Pool, Token, Faucet

network.connect('ropsten')
#network.connect('development')

names=['Riccardo','Matteo','Francesco','Diana','Cristiano']

Paycoin=Contract.from_abi("Paycoin",AddressesData['bot_minter']['paycoin'],Token.abi)
tokens=[Contract.from_abi("Tokens",AddressesData[f'{name}']['token'], Token.abi) for name in names]
ids=[AddressesData[f'{name}']['id']for name in names]
pools=[Contract.from_abi("Pools",AddressesData[f'{name}']['pool'], Pool.abi) for name in names]
token_names=[AddressesData[f'{name}']['token name'] for name in names]
token_symbols=[AddressesData[f'{name}']['token symbol'] for name in names]


admin_mnemonic = "rival purpose awkward protect knock almost effort eyebrow decade deputy science excess"
admin = accounts.from_mnemonic(admin_mnemonic)

today = date.today()
date = today.strftime("%m/%d/%Y")
block = web3.eth.get_block('latest')
block_number = block['timestamp']
json_file_name = str(today.strftime("%d") + "_data.json")

x = { f"{date}":{
         f"{block_number}":{
            "Becca":{
                token_names[0]:tokens[0].balanceOf(ids[0]),
                token_names[1]: tokens[1].balanceOf(ids[0]),
                token_names[2]:tokens[2].balanceOf(ids[0]),
                token_names[3]:tokens[3].balanceOf(ids[0]),
                token_names[4]:tokens[4].balanceOf(ids[0]),
                "paycoin": Paycoin.balanceOf(ids[0]),
                "token_Pool":tokens[0].balanceOf(pools[0]),
                "paycoin_Pool":Paycoin.balanceOf(pools[0]),
                "token_price":((tokens[0].balanceOf(pools[0]))/Paycoin.balanceOf(pools[0]))
                },
            "Citte":{
                token_names[0]:tokens[0].balanceOf(ids[1]),
                token_names[1]: tokens[1].balanceOf(ids[1]),
                token_names[2]:tokens[2].balanceOf(ids[1]),
                token_names[3]:tokens[3].balanceOf(ids[1]),
                token_names[4]:tokens[4].balanceOf(ids[1]),
                "paycoin": Paycoin.balanceOf(ids[1]),
                "token_Pool":tokens[1].balanceOf(pools[1]),
                "paycoin_Pool":Paycoin.balanceOf(pools[1]),
                "token_price":((tokens[1].balanceOf(pools[1]))/Paycoin.balanceOf(pools[1]))
                },
            "Francesco":{
                token_names[0]:tokens[0].balanceOf(ids[2]),
                token_names[1]: tokens[1].balanceOf(ids[2]),
                token_names[2]:tokens[2].balanceOf(ids[2]),
                token_names[3]:tokens[3].balanceOf(ids[2]),
                token_names[4]:tokens[4].balanceOf(ids[2]),
                "paycoin": Paycoin.balanceOf(ids[2]),
                "token_Pool":tokens[2].balanceOf(pools[2]),
                "paycoin_Pool":Paycoin.balanceOf(pools[2]),
                "token_price":((tokens[2].balanceOf(pools[2]))/Paycoin.balanceOf(pools[2]))
                },
            "Diana":{
                token_names[0]:tokens[0].balanceOf(ids[3]),
                token_names[1]: tokens[1].balanceOf(ids[3]),
                token_names[2]:tokens[2].balanceOf(ids[3]),
                token_names[3]:tokens[3].balanceOf(ids[3]),
                token_names[4]:tokens[4].balanceOf(ids[3]),
                "paycoin": Paycoin.balanceOf(ids[3]),
                "token_Pool":tokens[3].balanceOf(pools[3]),
                "paycoin_Pool":Paycoin.balanceOf(pools[3]),
                "token_price":((tokens[3].balanceOf(pools[3]))/Paycoin.balanceOf(pools[3]))
                },
             "Cristiano":{
                token_names[0]:tokens[0].balanceOf(ids[4]),
                token_names[1]: tokens[1].balanceOf(ids[4]),
                token_names[2]:tokens[2].balanceOf(ids[4]),
                token_names[3]:tokens[3].balanceOf(ids[4]),
                token_names[4]:tokens[4].balanceOf(ids[4]),
                "paycoin": Paycoin.balanceOf(ids[4]),
                "token_Pool":tokens[4].balanceOf(pools[4]),
                "paycoin_Pool":Paycoin.balanceOf(pools[4]),
                "token_price":((tokens[4].balanceOf(pools[4]))/Paycoin.balanceOf(pools[4]))
                },
            }
        }
    }
    
with open(json_file_name, "w") as write_file:
    json.dump(x, write_file, indent=4)

def write_json(new_data, date, block_number, filename=json_file_name):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data[date][block_number] = new_data
        file.seek(0)
        json.dump(file_data, file, indent = 4)

check=True
date_2=datetime.now()
currentTime = date_2.strftime("%H")

while(check==True and int(currentTime)<18):
    time.sleep(60)
    block = web3.eth.get_block('latest')
    if(block['timestamp']>=(block_number+10)):
        block_number=block['timestamp']
        print(f"Current Block in Ropsten: {block_number}")
        y = {f"{block_number}":{
                "Becca":{
                    token_names[0]:tokens[0].balanceOf(ids[0]),
                    token_names[1]: tokens[1].balanceOf(ids[0]),
                    token_names[2]:tokens[2].balanceOf(ids[0]),
                    token_names[3]:tokens[3].balanceOf(ids[0]),
                    token_names[4]:tokens[4].balanceOf(ids[0]),
                    "paycoin": Paycoin.balanceOf(ids[0]),
                    "token_Pool":tokens[0].balanceOf(pools[0]),
                    "paycoin_Pool":Paycoin.balanceOf(pools[0]),
                    "token_price":((tokens[0].balanceOf(pools[0]))/Paycoin.balanceOf(pools[0]))
                    },
                "Citte":{
                    token_names[0]:tokens[0].balanceOf(ids[1]),
                    token_names[1]: tokens[1].balanceOf(ids[1]),
                    token_names[2]:tokens[2].balanceOf(ids[1]),
                    token_names[3]:tokens[3].balanceOf(ids[1]),
                    token_names[4]:tokens[4].balanceOf(ids[1]),
                    "paycoin": Paycoin.balanceOf(ids[1]),
                    "token_Pool":tokens[1].balanceOf(pools[1]),
                    "paycoin_Pool":Paycoin.balanceOf(pools[1]),
                    "token_price":((tokens[1].balanceOf(pools[1]))/Paycoin.balanceOf(pools[1]))
                    },
                "Francesco":{
                    token_names[0]:tokens[0].balanceOf(ids[2]),
                    token_names[1]: tokens[1].balanceOf(ids[2]),
                    token_names[2]:tokens[2].balanceOf(ids[2]),
                    token_names[3]:tokens[3].balanceOf(ids[2]),
                    token_names[4]:tokens[4].balanceOf(ids[2]),
                    "paycoin": Paycoin.balanceOf(ids[2]),
                    "token_Pool":tokens[2].balanceOf(pools[2]),
                    "paycoin_Pool":Paycoin.balanceOf(pools[2]),
                    "token_price":((tokens[2].balanceOf(pools[2]))/Paycoin.balanceOf(pools[2]))
                    },
                "Diana":{
                    token_names[0]:tokens[0].balanceOf(ids[3]),
                    token_names[1]: tokens[1].balanceOf(ids[3]),
                    token_names[2]:tokens[2].balanceOf(ids[3]),
                    token_names[3]:tokens[3].balanceOf(ids[3]),
                    token_names[4]:tokens[4].balanceOf(ids[3]),
                    "paycoin": Paycoin.balanceOf(ids[3]),
                    "token_Pool":tokens[3].balanceOf(pools[3]),
                    "paycoin_Pool":Paycoin.balanceOf(pools[3]),
                    "token_price":((tokens[3].balanceOf(pools[3]))/Paycoin.balanceOf(pools[3]))
                    },
                 "Cristiano":{
                    token_names[0]:tokens[0].balanceOf(ids[4]),
                    token_names[1]: tokens[1].balanceOf(ids[4]),
                    token_names[2]:tokens[2].balanceOf(ids[4]),
                    token_names[3]:tokens[3].balanceOf(ids[4]),
                    token_names[4]:tokens[4].balanceOf(ids[4]),
                    "paycoin": Paycoin.balanceOf(ids[4]),
                    "token_Pool":tokens[4].balanceOf(pools[4]),
                    "paycoin_Pool":Paycoin.balanceOf(pools[4]),
                    "token_price":((tokens[4].balanceOf(pools[4]))/Paycoin.balanceOf(pools[4]))
                    },
                }
            }
        write_json(y, date, block_number)
       
