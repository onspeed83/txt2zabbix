import sys
from sys import argv
import requests
import json
import urllib3

urllib3.disable_warnings()

srv_group = '7' #required parameter
srv_templ_id = '10278'  #required parameter template ID  (in my case - Hepervisors)
create_enabled = 'false' # adding hosts disabled or enabled
zabbix_username = 'user'
zabbix_password = 'pass'
zabbix_url = 'LINK/api_jsonrpc.php'
headers = {'content-type': 'application/json'}  #leave as-is


filename = str(sys.argv[1])

f = open(filename)
f_input = f.read().split('\n')
f.close()
del f_input[0] #remove 1st string from file. Comment it, if you want to use first string (without description)

s = requests.Session()


auth_payload = {'jsonrpc': '2.0','method':'user.login','params':{'user':zabbix_username,'password':zabbix_password},'id':'1'}

r_auth = s.post(zabbix_url, data=json.dumps(auth_payload), headers=headers, verify=False)
result=r_auth.json()

#print(result)


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

    elif string_res[1] == 'SNMP':
        interface_type = '2' # SNMP

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
                        "port": srv_port,
                        "details": {
                            "version": 2,
                            "bulk": 1,
                            "community": "{$SNMP_COMMUNITY}"
                        }
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

    else:
         print('No interface type defined!')
         sys.exit()


    #print(json.dumps(create_payload))
    r_create = s.post(zabbix_url, data=json.dumps(create_payload), headers=headers, verify=False)

    #print(r_create.text)

    result = r_create.json()['result']
    host_ids = result['hostids'][0]
    print('Host created with ID: ', host_ids)  #creation result

    # enable or disable created hosts after creation
    if create_enabled == 'true':
        create_status = '0'

    elif create_enabled == 'false':
        create_status = '1'
    else:
        print('Error')
        sys.exit()

    upayload = {"jsonrpc": "2.0","method": "host.update","params": {"hostid": host_ids,"status": create_status},"auth": auth_key,"id": 1}
    r_upd = s.post(zabbix_url, data=json.dumps(upayload), headers=headers, verify=False)

requests.Session().close()
