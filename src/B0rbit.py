# -*- coding: utf-8 -*-

'''
Created on 03.06.2011

@author: alexander
'''

from HttpLogin import HttpLogin
from TCPPlayer import TCPPlayer
from GUI import OrbitGui

print("Starting up B0rbit v0.1")
usr = input("Username: ")
pwd = input("Password: ")
srv = input("Server: ")

print("Launching Bot. Please wait!")

gui = OrbitGui()

Login = HttpLogin(usr, pwd, srv)
FlashVars = Login.makeLogin()

print("FlashVars: ")
print(FlashVars)

TCP = TCPPlayer(FlashVars, gui)
