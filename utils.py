
class SetHosts:

#----------------------------------------------------
# Constructor
# Create IP list
#----------------------------------------------------
    def __init__ (self, q):

        a = 0
        while q.empty():
            a = a + 1
 
        self.ips = []
 
        while not q.empty():
            a = q.get()
            self.ips.append(a)
 
	self.ip_control = self.ips.pop()

#----------------------------------------------------
# Set Ansible host file
#
#----------------------------------------------------
    def set_ansible_hosts(self,f):

        f.write('[control]\n')

        f.write('{}\n'.format(self.ip_control))
        f.write('[work]\n')

        for i in range(0,len(self.ips)):
            ip = self.ips[i]
            f.write('{}\n'.format(ip))
 
        f.close()

#----------------------------------------------------
# Set remote etc/host
#
#----------------------------------------------------
    def set_remote_hosts(self,f,c):

        f.write("---\n")
        f.write("- hosts: {}\n".format(c))
        f.write("  remote_user: ubuntu\n")
        f.write("  sudo: yes\n")
        f.write("  tasks:\n")
        f.write("\n")
        f.write("  - name: add control IP to /etc/hosts\n")
        f.write("    lineinfile:\n")
        f.write("      dest: /etc/hosts\n")
        f.write("      insertafter: 'localhost$'\n")
        f.write("      line: '{} control'\n".format(self.ip_control))
        f.write("      state: present\n")

        for i in range(0,len(self.ips)):
            ip = self.ips[i]
            f.write("\n")

            f.write("  - name: add control IP to /etc/hosts\n")
            f.write("    lineinfile:\n")
            f.write("      dest: /etc/hosts\n")
            f.write("      insertafter: 'localhost$'\n")
            f.write("      line: '{} work{}'\n".format(ip,i+1))
            f.write("      state: present\n")
            f.write("\n")

        f.close()

#----------------------------------------------------
# Exchange SSH keys
#
#----------------------------------------------------
    def set_keys(self,f,path):

        f.write("---\n")
        f.write("- hosts: {}\n".format(self.ip_control))
        f.write("  remote_user: ubuntu\n")
        f.write("  sudo: yes\n")
        f.write("  tasks:\n")
        f.write("\n")
        f.write("  - name: download control key\n")
        f.write("    fetch: src=/home/cluster/.ssh/id_rsa.pub dest={}id_rsa0.pub  flat=yes\n".format(path))

        for i in range(0,len(self.ips)):
            ip = self.ips[i]
            f.write("\n")

            f.write("- hosts: {}\n".format(ip))
            f.write("  remote_user: ubuntu\n")
            f.write("  sudo: yes\n")
            f.write("  tasks:\n")
            f.write("\n")

            f.write("  - name: download work1 key\n")
            f.write("    fetch: src=/home/cluster/.ssh/id_rsa.pub dest={}id_rsa{}.pub  flat=yes\n".format(path,i+1))

            f.write("\n") 
            f.write("  - name: update work{} authorized key\n".format(i+1))
            f.write("    authorized_key: user=cluster key=\"{{ item }}\" state=present\n")
            f.write("    with_file:\n")
            f.write("      - id_rsa0.pub\n")

        f.write("\n") 
        f.write("- hosts: {}\n".format(self.ip_control))
        f.write("  remote_user: ubuntu\n")
        f.write("  sudo: yes\n")
        f.write("  tasks:\n")

        for i in range(0,len(self.ips)):
            ip = self.ips[i]
            f.write("\n")

            f.write("  - name: update control authorized key\n")
            f.write("    authorized_key: user=cluster key=\"{{ item }}\" state=present\n")
            f.write("    with_file:\n")
            f.write("      - id_rsa{}.pub\n".format(i+1))


        f.close()

#----------------------------------------------------
# Clean up control node
#
#----------------------------------------------------
    def clean_control(self,f):

        f.write("---\n")
        f.write("- hosts: control\n")
        f.write("  remote_user: ubuntu\n")
        f.write("  sudo: yes\n")
        f.write("  tasks:\n")
        f.write("\n")

        f.write("  - name: Create MPI hosts file\n")
        f.write("    file: path=/home/cluster/hosts state=touch\n")
        f.write("\n")

        for i in range(0,len(self.ips)):
            f.write("  - name: Write to hosts\n")
            f.write("    lineinfile: dest=/home/cluster/hosts line=\"work{}\"\n".format(i+1))
            f.write("\n")

        for i in range(0,len(self.ips)):
            ip = self.ips[i]
            f.write("  - name: Write work{} to NFS /etc/exports\n".format(i+1))
            f.write("    lineinfile: dest=/etc/exports line=\"/home/cluster/bin {}(rw,sync,no_subtree_check)\"".format(ip))
            f.write("\n")

        f.write("\n")
        f.write("  - name: Restart NFS\n")
        f.write("    command: exportfs -a\n")
        f.write("    command: service nfs-kernel-server start\n")

        f.close()

#----------------------------------------------------
# Clean up work node
#
#----------------------------------------------------
    def clean_work(self,f):

        f.write("---\n")
        f.write("- hosts: work\n")
        f.write("  remote_user: ubuntu\n")
        f.write("  sudo: yes\n")
        f.write("  tasks:\n")
        f.write("\n")

        f.write("  - name: Mount NFS\n")
        f.write("    command: mount {}:/home/cluster/bin /home/cluster/bin".format(self.ip_control))

        f.close()


