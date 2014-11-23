#!/usr/bin/env python

# Copyright (C) 2014 Devesh Saini(futuredevesh@gmail.com).
#
# This file is part of Pyexplorer.
#
#     Pyexplorer is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Pyexplorer is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Pyexplorer.  If not, see <http://www.gnu.org/licenses/>.

import json
import curses
from string import printable, uppercase, lowercase

def _load_(keybind_file):
	
	keybind_dump = open(keybind_file, 'r')

	unicode_keybinds = json.load(keybind_dump)	

	keybind_dump.close()

	return unicode_keybinds

def _unicode_to_str_(unicode_keybinds):

	keybinds = {}

	keybinds_keys = [str(x) for x in unicode_keybinds.keys()]
	keybinds_values = [str(y) for y in unicode_keybinds.values()]

	for x, y in zip(keybinds_keys, keybinds_values):

		keybinds[x] = y

	return keybinds

def _get_curses_keys_(str_keybinds):

	keybinds = {}

	for key, value in zip(str_keybinds.keys(), str_keybinds.values()):
		
		try: keybinds[key] = getattr(curses, value)

		except: keybinds[key] = value

	return keybinds

def _replace_special_values_(keybinds):

	#Replacing value of "quit".
	quit = keybinds['quit']

	if len(quit)==1 and quit in printable:

		keybinds['quit'] = ord(keybinds['quit'])

	else:

		raise ValueError("Value/length of \"quit\" is invalid. Length should be 1 and value should be an alphabet, number or any special character.")

	#Replacing value of "Jumper_alphabets"
	if keybinds["Jumper_alphabets"]=="uppercase":

		keybinds_printable = filter(lambda x: x not in lowercase, printable) #Excluding lowercase characters.

		keybinds['Jumper_alphabets'] = keybinds_printable

	elif keybinds["Jumper_alphabets"]=="lowercase":
		
		keybinds_printable = filter(lambda x: x not in uppercase, printable) #Excluding uppercase characters.

		keybinds['Jumper_alphabets'] = keybinds_printable

	else:
		raise ValueError("\"Jumper_alphabets\" value - \""+keybinds["Jumper_alphabets"]+"\" is invalid. It should be \"uppercase\" or \"lowercase\"")

	return keybinds

def _define_variables_(keybinds):

	for key, value in zip(keybinds.keys(), keybinds.values()):

		globals()[key] = value

def load_keybinds():

	unicode_keybinds = _load_('keybinds') #Loading keybindings from JSON file.

	str_keybinds = _unicode_to_str_(unicode_keybinds) #Converting obtained keybindings keys and values to "str" data type since the default state of keybindings is "unicode"
	
	cursed_keybinds = _get_curses_keys_(str_keybinds) #Replacing every replacable values of str_keybinds to the value of "curses.value" eg:- str_keybinds["MoveUp"] is "KEY_UP"(By default), now, this value is replaced by the value of curses.KEY_UP

	keybinds = _replace_special_values_(cursed_keybinds) #Replaces few values individually since they can't be replaced as a bulk.

	_define_variables_(keybinds) #Now defines every key:value pair as variable=value in global scope.

	return keybinds #Returning keybinds 'dict' variable too.
