#!/usr/bin/env python

import os
from ftputil import FTPHost
import sys
from termcolor import colored

def _check_arguments_(arguments):

	invalid_arguments = [] #Will contain 'key' if value in that key:value pair is invalid.

	#Checking for normal arguments.
	for arg in arguments.keys():

		try: #Try-except here since there are some arguments(keys) which are not defined in allowed_arguments. So, allowed_args[arg] will cause error.

			if not arguments[arg] in allowed_args[arg]:

				invalid_arguments.append(arg)

		except KeyError: pass

	#Cheking for directory existence.
	try: #try-except since 'origin' may not exist in arguments dict.
		
		try:
			if not arguments['use']=='ftp':
				if not os.path.isdir(arguments['origin']):
					invalid_arguments.append('origin')
		except:

			if not os.path.isdir(arguments['origin']):

				invalid_arguments.append('origin')

	except KeyError: pass

	try: #try-except since 'buff' i.e. 'buffer' may not exist in arguments dict.

		if not (arguments['buff'] in ['page'] or arguments['buff'].isdigit()):

			invalid_arguments.append('buff')

	except KeyError: pass

	if len(invalid_arguments)==0: #No invalid arguments, returns a tuple containing True at 0th positions
		return (False, None)

	else: #Invalid arguments exist, returns a tuple containing 'False' at 0th position.
		return (True, invalid_arguments)

def _invalid_arg_reporter_(arguments, invalid_arguments, do_exit=False): #On printing arguments, if exit is True, then exists the applications.

	os.system("clear")

	print "\n Please check your argument values:- \n"

	for index, arg in enumerate(arguments.keys()):

		if arg in invalid_arguments:
			print " "+str(index+1)+". "+arg+"="+colored(arguments[arg], color='white', on_color='on_red') #Print the key first and value with 'red' background. eg:- key=red_colored(value). It's red because this value will always be wrong.

		else:
			print " "+str(index+1)+". "+arg+"="+colored(arguments[arg], color='white', on_color='on_green') #Print the key first and value with 'green' background eg:- key=green_colored(value). It's red because this value will always be right.

	if do_exit:

		print #A horizontal space before leaving.
		exit()

def _change_types_(arguments):

	for key in arguments.keys():

		value = arguments[key]

		#Changing to boolean value if 'value' can be changed to boolean i.e. if 'value' is "True" or "False" written as strings.
		if value in ("True", "true", 1):
			arguments[key] = True

		elif value in ("False", "false", 0):
			arguments[key] = False

		#Changing to integer value if 'value' can be changed to integer i.e. if 'value' is a integer written as string.
		try: 
			arguments[key] = int(value)

		except:continue

	return arguments

def getargs(argv):

	#Setting up command-line arguments below.

	str_booleans = ("True", "true", '1', "False", "false", '0') #A variable containing set of string versions of boolean "True" and "False".

	global allowed_args

	if len(argv[1:])>0: #If user has given arguments
				
		arguments = {} # An key:value version of command-line arguments i.e. argv[1:]

		for arg in argv[1:]: #Leaving the first element i.e. the filename.

			key, value = arg.split('=')
			arguments[key] = value

		allowed_args = {'show_hidden': str_booleans, 'parent_navigation': str_booleans} #These are the possible arguments and their respective possible values.

		invalid_arguments = _check_arguments_(arguments)

		if invalid_arguments[0]: #The first index i.e. 0th index will always be a boolean value i.e. True or False as defined in function _check_arguments_()

			_invalid_arg_reporter_(arguments, invalid_arguments[1], do_exit=True) # do exit if their is even one invalid argument value present.

		arguments = _change_types_(arguments) #Changing types if possible. Read comment inside that function.

		return arguments

	else: return () #Returns an zero length tuple.

if __name__=="__main__":

	print getargs(sys.argv)
