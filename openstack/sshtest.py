from __future__ import print_function
import os, socket, sys
from novaclient.client import Client as NovaClient
import time
def isOpen(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
                s.connect((ip, int(port)))
                s.shutdown(socket.SHUT_RDWR)
                return True
        except:
                return False
        finally:
                s.close()

username=os.getenv('OS_USERNAME')
password=os.getenv('OS_PASSWORD')
auth_url=os.getenv('OS_AUTH_URL')
project_name=os.getenv('OS_TENANT_NAME')
region_name=os.getenv('OS_REGION_NAME')

novaclient = NovaClient('2', username=username, password=password, auth_url=auth_url, project_name=project_name, region_name=region_name)

vms=novaclient.servers.list(search_opts={'all_tenants': 1,'status': 'ACTIVE'})

count = 1
results = {}
for vm in vms:

    print(str(count)+' of '+str(len(vms)),end='\r')
    sys.stdout.flush()
    count = count + 1
    for key in vm.addresses:
            floatingip = 'NA'
            nics = vm.addresses[key]
            for nic in nics:
                if nic['OS-EXT-IPS:type'] == 'floating':
                    floatingip = nic['addr']
                    break

    hypervisor = getattr(vm, 'OS-EXT-SRV-ATTR:hypervisor_hostname')
    port_test = True
    iplist = []
    if( floatingip != 'NA' ):
        port_test = isOpen(floatingip, 22)


    if( results.has_key(hypervisor) == False):
        results[hypervisor] = { 'active': 0,  'iplist': []}
    
    results[hypervisor]['active'] = results[hypervisor]['active'] + 1
    if ( port_test == False):
         results[hypervisor]['iplist'].append(floatingip)


print('Compute      Activevms    Failedvms      IpList')
for hypervisor in results:
    if(len(results[hypervisor]['iplist']) != 0):
        print(hypervisor, results[hypervisor]['active'], len(results[hypervisor]['iplist']), results[hypervisor]['iplist'])
