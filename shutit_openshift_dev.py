"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class shutit_openshift_dev(ShutItModule):


	def build(self, shutit):
		# Some useful API calls for reference. See shutit's docs for more info and options:
		#
		# ISSUING BASH COMMANDS
		# shutit.send(send,expect=<default>) - Send a command, wait for expect (string or compiled regexp)
		#                                      to be seen before continuing. By default this is managed
		#                                      by ShutIt with shell prompts.
		# shutit.multisend(send,send_dict)   - Send a command, dict contains {expect1:response1,expect2:response2,...}
		# shutit.send_and_get_output(send)   - Returns the output of the sent command
		# shutit.send_and_match_output(send, matches) 
		#                                    - Returns True if any lines in output match any of 
		#                                      the regexp strings in the matches list
		# shutit.send_until(send,regexps)    - Send command over and over until one of the regexps seen in the output.
		# shutit.run_script(script)          - Run the passed-in string as a script
		# shutit.install(package)            - Install a package
		# shutit.remove(package)             - Remove a package
		# shutit.login(user='root', command='su -')
		#                                    - Log user in with given command, and set up prompt and expects.
		#                                      Use this if your env (or more specifically, prompt) changes at all,
		#                                      eg reboot, bash, ssh
		# shutit.logout(command='exit')      - Clean up from a login.
		# 
		# COMMAND HELPER FUNCTIONS
		# shutit.add_to_bashrc(line)         - Add a line to bashrc
		# shutit.get_url(fname, locations)   - Get a file via url from locations specified in a list
		# shutit.get_ip_address()            - Returns the ip address of the target
		# shutit.command_available(command)  - Returns true if the command is available to run
		#
		# LOGGING AND DEBUG
		# shutit.log(msg,add_final_message=False) -
		#                                      Send a message to the log. add_final_message adds message to
		#                                      output at end of build
		# shutit.pause_point(msg='')         - Give control of the terminal to the user
		# shutit.step_through(msg='')        - Give control to the user and allow them to step through commands
		#
		# SENDING FILES/TEXT
		# shutit.send_file(path, contents)   - Send file to path on target with given contents as a string
		# shutit.send_host_file(path, hostfilepath)
		#                                    - Send file from host machine to path on the target
		# shutit.send_host_dir(path, hostfilepath)
		#                                    - Send directory and contents to path on the target
		# shutit.insert_text(text, fname, pattern)
		#                                    - Insert text into file fname after the first occurrence of 
		#                                      regexp pattern.
		# shutit.delete_text(text, fname, pattern)
		#                                    - Delete text from file fname after the first occurrence of
		#                                      regexp pattern.
		# shutit.replace_text(text, fname, pattern)
		#                                    - Replace text from file fname after the first occurrence of
		#                                      regexp pattern.
		# ENVIRONMENT QUERYING
		# shutit.host_file_exists(filename, directory=False)
		#                                    - Returns True if file exists on host
		# shutit.file_exists(filename, directory=False)
		#                                    - Returns True if file exists on target
		# shutit.user_exists(user)           - Returns True if the user exists on the target
		# shutit.package_installed(package)  - Returns True if the package exists on the target
		# shutit.set_password(password, user='')
		#                                    - Set password for a given user on target
		#
		# USER INTERACTION
		# shutit.get_input(msg,default,valid[],boolean?,ispass?)
		#                                    - Get input from user and return output
		# shutit.fail(msg)                   - Fail the program and exit with status 1
		# 
		shutit.send('mkdir -p $GOPATH/src/github.com/openshift')
		shutit.send('cd $GOPATH/src/github.com/openshift')
		shutit.send('rm -rf origin')
		shutit.send('git clone git@github.com:ianmiell/origin')
		shutit.send('cd origin')
		shutit.send('git remote add upstream git://github.com/openshift/origin')
		shutit.send('export OPENSHIFT_MEMORY=4192')
		shutit.send('vagrant up')
		shutit.login(command='vagrant ssh')
		shutit.login(password='vagrant')
		shutit.install('xterm')
		shutit.send('export PATH=/data/src/github.com/openshift/origin/_output/local/go/bin/linux/amd64:/data/src/github.com/openshift/origin/_output/local/go/bin:$PATH')
		shutit.send('cd /data/src/github.com/openshift/origin')
		shutit.send('make clean build')
		# update path to include binaries for oc, oadm, etc
		# this is temporary, to make it persistent add it to .bash_profile
		# redirect the logs to  /home/vagrant/openshift.log for easier debugging
		# TODO: make this configurable, defaulting to localhost instead of shutit.tk
		server = 'localhost'
		server = 'shutit.tk'
		#shutit.send('sudo `which openshift` start --public-master=' + server + ' --write-config=openshift.local.config &> openshift.log &')
		shutit.send('sudo `which openshift` start --public-master=' + server + ' &> openshift.log &')
		shutit.send_until('ls openshift.local.config/master/openshift-registry.kubeconfig | wc -l','1')
		shutit.send('mkdir -p ~/.kube')
		shutit.send('cp openshift.local.config/master/admin.kubeconfig ~/.kube/config')
		shutit.send('sudo chmod +r openshift.local.config/master/openshift-registry.kubeconfig')
		shutit.send('sudo chmod +r openshift.local.config/master/admin.kubeconfig')
		shutit.send('oadm registry --create --credentials=openshift.local.config/master/openshift-registry.kubeconfig --config=openshift.local.config/master/admin.kubeconfig')
		# load image stream
		shutit.send('oc create -f examples/image-streams/image-streams-centos7.json -n openshift --config=openshift.local.config/master/admin.kubeconfig')
		# load templates
		shutit.send('oc create -f examples/sample-app/application-template-stibuild.json -n openshift --config=openshift.local.config/master/admin.kubeconfig')
		shutit.send('oc create -f examples/db-templates --config=openshift.local.config/master/admin.kubeconfig')
		# TODO: set the config up, change hostname to shutit.tk, copy kubeconfig so that we can be admin
		shutit.send('echo now navigate to: https://localhost:8443/console')
		shutit.pause_point('')
		shutit.logout()
		shutit.logout()
		return True

	def get_config(self, shutit):
		# CONFIGURATION
		# shutit.get_config(module_id,option,default=None,boolean=False)
		#                                    - Get configuration value, boolean indicates whether the item is 
		#                                      a boolean type, eg get the config with:
		# shutit.get_config(self.module_id, 'myconfig', default='a value')
		#                                      and reference in your code with:
		# shutit.cfg[self.module_id]['myconfig']
		return True

	def test(self, shutit):
		# For test cycle part of the ShutIt build.
		return True

	def finalize(self, shutit):
		# Any cleanup required at the end.
		return True
	
	def is_installed(self, shutit):
		return False


def module():
	return shutit_openshift_dev(
		'shutit.tk.shutit_openshift_dev.shutit_openshift_dev', 782914092.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit-library.virtualbox.virtualbox.virtualbox','tk.shutit.vagrant.vagrant.vagrant']
	)

