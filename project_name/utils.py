import binascii
import os

def capname(name):
    if ' ' not in name:
        return name.capitalize()
    return name

def random_key(bytesize=16):
    return binascii.hexlify(os.urandom(bytesize)).decode('ascii')
