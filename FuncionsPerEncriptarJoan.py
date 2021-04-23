#-*-encoding: utf8-*-
#!/usr/bin/env python
import Crypto
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from base64 import b64encode, b64decode
import hashlib
from Crypto.Random import random
from Crypto import Random
from Crypto.Cipher import AES
import base64

import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes


import json
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
#aquesta funció genera un parell de claus RSA de 2048 bytes i les retorna.
def generate_RSA():
    claus = RSA.generate(2048)
    return claus

#aquesta funció exporta una clau en un fitxer .pem
def export_key_RSA(ruta, claus):

    fitxerAmbClauExportada = open(ruta, "wb")
    clauExportada = claus.export_key()
    fitxerAmbClauExportada.write(clauExportada)

#aquesta funció importa una clau
def import_key_RSA(ruta):

    fitxerAmbClauExportada = open(ruta, "r")
    clau = fitxerAmbClauExportada.read()
    clau = RSA.import_key(clau)
    return clau

#aquesta funció encripta un missatge mitjançant RSA
def encript_message_RSA(missatge, clau):

    missatge = missatge.encode()
    a = PKCS1_OAEP.new(clau)
    missatgeEncriptat = a.encrypt(missatge)
    return missatgeEncriptat

#aquesta funció desencripta un missatge mitjançant RSA
def decript_message_RSA(missatge, clau):

    a = PKCS1_OAEP.new(clau)
    missatgeDesencriptat = a.decrypt(missatge)
    return missatgeDesencriptat.decode()

#aquesta funció genara una clau a partir de SHA256 i la retorna
def generate_AES(contra):
    claus = hashlib.new("SHA256",contra.encode())
    return claus.digest()

#aquesta funció encripta un missatge mitjançant AES en mode CBC
def encript_message_AES(missatge, clau):
    encoding = 'utf-8'
    missatge=missatge.encode()
    cipher = AES.new(clau, AES.MODE_CBC)
    missatgeEncriptat = cipher.encrypt(pad(missatge, AES.block_size))
    missatgeEncriptat = cipher.iv + missatgeEncriptat
    return missatgeEncriptat


#aquesta funció desencripta un missatge mitjançant AES en mode CBC
def decript_message_AES(missatge, clau):


    iv = missatge[0:16]
    ct = missatge[16:]

    cipher = AES.new(clau, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt







#bytes a string == b64encode(variable).decode()
#string a bytes == b64decode(variable.encode())
