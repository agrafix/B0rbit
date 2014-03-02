# -*- coding: utf-8 -*-

'''
Created on 10.06.2011

@author: alexander
'''

from cx_Freeze import setup, Executable

setup(
        name = "B0rbit",
        version = "0.1",
        description = "Bot for DO",
        executables = [Executable("B0rbit.py")])