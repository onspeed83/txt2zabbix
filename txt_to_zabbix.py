#!/usr/bin/env python3
#Simple and ugly script for adding hosts to zabbix from text file using zabbix api
# written for zabbix 4.2 

import sys
from sys import argv
import requests
import json



srv_group = '7' #required parameter
srv_templ_id = '10278'  #required parameter template ID  (in my case - Hepervisors)

create_enabled = 'false' # adding hosts disabled or enabled

zabbix_username = 'zabbix_username'
zabbix_password = 'zabbix_password'
zabbix_url = 'http://zabbix_server_ip/api_jsonrpc.php'  

headers = {'content-type': 'application/json'}


filename = str(sys.argv[1])

f = open(filename)
f_input = f.read().split('\n') 
f.close()
del f_input[0] #remove 1st string from file.

s = requests.Session()


auth_payload = {'jsonrpc': '2.0','method':'user.login','params':{'user':zabbix_username,'password':zabbix_password},'id':'1'}

r_auth = s.post(zabbix_url, data=json.dumps(auth_payload), headers=headers, verify=False,)
result=r_auth.json()
auth_key=result['result'] # getting authorization key  from zabbix



for i in f_input:

    string_res = i.split();  
    

    srv_name = string_res[0]
    srv_type = string_res[1]
    srv_ip = string_res[2]
    srv_port = string_res[3]
    
    #choosing tipe of host's interface
    if string_res[1] == 'Agent':
        interface_type = '1'        
    elif string_res[1] == 'SNMP':
        interface_type = '2' # SNMP
    else:
         print('No interface type defined!')
         sys.exit()

    create_payload = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": srv_name,
                "interfaces": [
                    {
                        "type": interface_type,
                        "main": 1,
                        "useip": 1,
                        "ip": srv_ip,
                        "dns": "",
                        "port": srv_port
                    }
                ],
                "groups": [
                    {
                        "groupid": srv_group
                    }
                ],
                "templates": [
                    {
                        "templateid": srv_templ_id
                    }
                ],
            },
            "auth": auth_key,
            "id": 1
        }

    r_create = s.post(zabbix_url, data=json.dumps(create_payload), headers=headers, verify=False,)
    
    #print(r_create.text)
    
    result = r_create.json()['result']
    host_ids = result['hostids'][0]
    print('Создан хост с ID: ', host_ids)  #creation result

    # enable or disable created hosts after creation
    if create_enabled == 'true':
        create_status = '0'

    elif create_enabled == 'false':
        create_status = '1'
    else:
        print('Ошибка')
        sys.exit()

    upayload = {"jsonrpc": "2.0","method": "host.update","params": {"hostid": host_ids,"status": create_status},"auth": auth_key,"id": 1}
    r_upd = s.post(zabbix_url, data=json.dumps(upayload), headers=headers, verify=False,)

requests.Session().close()
