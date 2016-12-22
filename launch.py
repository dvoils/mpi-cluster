import boto.ec2
import time
from subprocess import call
import multiprocessing as mp
import random

from utils import SetHosts

def launch_instance(access_key, secret_key): 

    my_instance = conn.run_instances('ami-86e0ffe7', key_name='id_rsa', instance_type='t1.micro', security_groups=['cluster'])

    # Get instance meta information
    #
    meta = my_instance.instances[0]

    # Wait for the instance to start
    #
    print('Waiting for instance to start')
    state = meta.state
    while state != 'running':
        time.sleep(2)
        state = meta.update()

    # Wait for the instance to boot
    #
    print('Waiting for instance to boot')
    status = 'temp'
    while status != 'passed':
        my_id = str(meta.id)
        time.sleep(2)
        a = conn.get_all_instance_status(instance_ids=my_id)
        b = a[0].system_status.details
        status = str(b['reachability'])

    # Get the IP address
    #
    my_ip = meta.ip_address
    q.put(my_ip)

if __name__ == '__main__':

    access_key='id'
    secret_key='key'

    # Connect to region
    #
    conn = boto.ec2.connect_to_region("us-west-2",
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key)

    # Launch instances
    #
    p = []
    q = mp.Queue()

    for x in range(0, 4):
        launch = mp.Process(target=launch_instance, args=(access_key, secret_key))
        launch.start()
        p.append(launch)

    for process in p:
        print('Process Complete: {}'.format(process))
        process.join()

    for process in p:
        print('Process Terminate: {}'.format(process))
        process.terminate()

    # Set up host info
    #
    sethosts = SetHosts(q)

    f1 = open('hosts', 'w')
    f2 = open('/control/hosts.yml', 'w')
    f3 = open('/work/hosts.yml', 'w')
    f4 = open('keys.yml', 'w')
    f5 = open('/control/cleanup.yml', 'w')
    f6 = open('/work/cleanup.yml', 'w')
    path = "./"

    sethosts.set_ansible_hosts(f1)
    sethosts.set_remote_hosts(f2,"control")
    sethosts.set_remote_hosts(f3,"work")
    sethosts.set_keys(f4,path)
    sethosts.clean_control(f5)
    sethosts.clean_work(f6)

    # Run the playbooks
    #
    time.sleep(2)
    call(["ansible-playbook", "control/user.yml"])
    call(["ansible-playbook", "work/user.yml"])
    call(["ansible-playbook", "control/hosts.yml"])
    call(["ansible-playbook", "work/hosts.yml"])
    call(["ansible-playbook", "keys.yml"])
    call(["ansible-playbook", "control/setup.yml"])
    call(["ansible-playbook", "work/setup.yml"])
    call(["ansible-playbook", "control/cleanup.yml"])
    call(["ansible-playbook", "work/cleanup.yml"])



