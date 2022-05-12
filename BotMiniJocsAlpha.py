import json
import requests
import telebot
from telebot import types

import random
import sqlite3
import re
import time

#encriptar
from FuncionsPerEncriptarJoan import *

#correu
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#process
from multiprocessing import Process
from threading import Thread


TOKEN = ''

#variables comprobacions
contestat = False
#register estats
ESPERANT_CORREU = 0
ESPERANT_CONTRA = 1
REGISTRAT = 2

#jocs estats
JUGANT = 0
PARTIDA_ACABADA = 1


#diccionari estats
estatsRegister = {}
estatsTresEnRatlla = {}
estatsDaus = {}

#tresEnRatlla variables

fitxesTauler = [" ", "1","2","3","4","5","6","7","8","9","10"] 
numTirades = 0

#daus variables

numMaquina = 0

#base de dades

con = sqlite3.connect('botTelegram.db', check_same_thread=False)
cursorObjecte = con.cursor()

#creem les taules de la base de dades
try:
    cursorObjecte.execute("""  CREATE TABLE USUARIS(
            CID INTEGER PRIMARE KEY NOT NULL,
            CORREU TEXT,
            CONTRASENYA TEXT,
            PUNTUACIO INTEGER
        )  """)

    con.commit()
except sqlite3.OperationalError:
    pass




#register variables
nomUsuari = ""
contrasenya = ""

bot = telebot.TeleBot(TOKEN, threaded=True)


comandos = {
    'start'       : 'Inicia el bot',
    'ajuda'       : 'Et mostra una llista amb tots els comandos',
    'jugar'       : 'Et mostra una llista de tots els jocs. ',
    'puntuacio'   : 'Mostra la quantitat de punts que tens (cada cop que guanyes una partida a qualsevol joc, guanyes un punt) ',
    'registrar'   : 'Crear-te un nou usuari. ',
    'borrarUsuari': 'Borrar l\'usuari actual ',
    'correu'      : "T'envia un correu amb la quantitat de punts que tens acumulats "
}

jocs = {
    'tresEnRatlla' : "En aquest joc tindras d'anar posant fitxes en un tauler, quan algu tingui 3 fitxes en ratlla guanyarà la partida.  ",
    'daus'         : "Aquest joc consisteix en tirar els daus, si treus un numero mes alt que el contrincant guanyes.  "
}



def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)




@bot.message_handler(commands=['ajuda'])
def comando_ajuda(m):
    cid = m.chat.id

    missatgeAjuda = "Pots executar algun dels següents comandos: \n"
    for comando in comandos:
         missatgeAjuda += "/" + comando + ": "
         missatgeAjuda += comandos[comando] + "\n"

    bot.send_message( cid, missatgeAjuda)


@bot.message_handler(commands=['jugar'])
def comando_jugar(m):
    cid = m.chat.id
    missatgeAjuda = "Pots jugar algun dels següents jocs:  \n"
    for joc in jocs:
         missatgeAjuda += "/" + joc + ": "
         missatgeAjuda += jocs[joc] + "\n"

    bot.send_message(cid, missatgeAjuda)


@bot.message_handler(commands=['registrar'])
def comando_registrar(m):
    cid = m.chat.id
    if not comprobarRegistre(cid):
        estatsRegister[cid] = ESPERANT_CORREU
        missatge = " Introdueix el teu correu: \n"
        bot.send_message(cid, missatge)

        #fill per si es tarda molt a contestar
        registrar = Thread(target=contarSegons, args=[cid,])
        registrar.start()
    else:
        missatge = "Ja estas registrat. Només es pot tenir un usuari per cada compte de telegram. Si vols crear-te una nova compta utilitza /borrarUsuari per eliminar el compte actual "
        bot.send_message(cid, missatge)



def demanarContra(cid):
    global contestat
    missatge = " Introdueix la contrasenya:  \n"
    bot.send_message(cid, missatge)

    #fill per si es tarda molt a contestar
    contestat = False
    registrar2 = Thread(target=contarSegons, args=[cid,])
    registrar2.start()


@bot.message_handler(commands=['puntuacio'])
def comando_puntuacions(m):
    cid = m.chat.id

    if comprobarRegistre(cid):
        cursorObjecte.execute('SELECT PUNTUACIO FROM USUARIS where CID =  ' + str(cid))
        puntuacio = cursorObjecte.fetchall()
        puntuacioStr = str(puntuacio[0][0])
    
        missatge = "De moment tens un total de " + puntuacioStr + " punts. "
        bot.send_message(cid, missatge)
    else:
        missatge = "Primer et tens de registrar!!!! Utilitza /registrar."
        bot.send_message(cid, missatge)

@bot.message_handler(commands=['borrarUsuari'])
def comando_borrar(m):
    cid = m.chat.id
    if comprobarRegistre(cid):
        cursorObjecte.execute('DELETE FROM USUARIS where CID =  ' + str(cid))
        con.commit()
    
        missatge = "Usuari borrat!!!"
        bot.send_message(cid, missatge)
    else:
        missatge = "Primer et tens de registrar!!!! Utilitza /registrar."
        bot.send_message(cid, missatge)



@bot.message_handler(commands=['correu'])
def comando_correu(m):
    cid = m.chat.id
    if comprobarRegistre(cid):
        cursorObjecte.execute('SELECT CORREU, PUNTUACIO FROM USUARIS where CID =  ' + str(cid))
        correu = cursorObjecte.fetchall()
        correuStr = str(correu[0][0])
        punts = str(correu[0][1])
        
        msg = MIMEMultipart()
        missatgePunts = "De moment tens un total de " + punts + " punts. "

        #parametres per configurar correu  
        password = "botTelegram1234"
        msg['From'] = "correuBotTelegram@gmail.com"
        msg['To'] = correuStr
        msg['Subject'] = "Bot Telegram Punts"
        
        #afeguim el missatge
        msg.attach(MIMEText(missatgePunts, 'plain'))
        
        #creem el server
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        
        #iniciem sessio a la nostre compte
        server.login(msg['From'], password)
        
        
        #enviem el missatge
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        
        server.quit()



    
        missatge = "Correu enviat correctament!!! S'ha enviat a " + str(correuStr)
        bot.send_message(cid, missatge)
    else:
        missatge = "Primer et tens de registrar!!!! Utilitza /registrar."
        bot.send_message(cid, missatge)


#jocs


#tresEnRatlla
@bot.message_handler(commands=['tresEnRatlla'])
def comando_trenEnRatlla(m):
    cid = m.chat.id
    
    if comprobarRegistre(cid):
        #tauler
        mostrarTauler(cid)
        missatge = "Introdueix la posició on vols colocar la fitxa: "

        estatsTresEnRatlla[cid] = JUGANT
        bot.send_message(cid, missatge)

        #fill per si es tarda molt a contestar
        contestat = False
        tresEnRatlla = Thread(target=contarSegons, args=[cid,])
        tresEnRatlla.start()

    else:
        missatge = "Primer et tens de registrar!!!! Utilitza /registrar."
        bot.send_message(cid, missatge)

#joc daus
@bot.message_handler(commands=['daus'])
def comando_daus(m):
    global numMaquina
    cid = m.chat.id

    if comprobarRegistre(cid):
        estatsDaus[cid] = JUGANT

        numMaquina = random.randint(1, 6)

        missatge = "La màquina ha tret un " + str(numMaquina)
        bot.send_message(cid, missatge)

        missatge = "Introdueix qualsevol caràcter per llençar el teu dau: " 
        bot.send_message(cid, missatge)

        #fill per si es tarda molt a contestar
        contestat = False
        daus = Thread(target=contarSegons, args=[cid,])
        daus.start()


    else:
        missatge = "Primer et tens de registrar!!!! Utilitza /registrar."
        bot.send_message(cid, missatge)

#missatjes sense comando
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    cid = m.chat.id
    global numTirades
    global fitxesTauler
    global numMaquina
    global contestat

    if cid in estatsRegister and estatsRegister[cid] == ESPERANT_CORREU:
        correu = m.text
        #comprovo que el correu sigui valid
        if correuValid(correu):
            #guardo el cprreu a la base de dades
            cursorObjecte.execute("INSERT INTO USUARIS VALUES(" + str(cid) + ", \"" +  correu + "\", \"\", 0)")
            con.commit()
            estatsRegister[cid] = ESPERANT_CONTRA
            contestat = True
            demanarContra(cid)
        else:
            bot.send_message(cid, "Correu no vàlid. ")


        
    elif cid in estatsRegister and estatsRegister[cid] == ESPERANT_CONTRA:
        estatsRegister[cid] = REGISTRAT
        contrasenya = m.text

        #encriptarContra
        clauAES =  generate_AES(contrasenya)
        contraEncriptada = encript_message_AES(contrasenya, clauAES)
    
        #guardem la contra a la base de dades
        cursorObjecte.execute("UPDATE USUARIS SET CONTRASENYA = '" + contrasenya + "' where CID = " + str(cid))
        con.commit()
        contestat = True
        bot.send_message(cid, "Registrat correctament!!! ")
        bot.delete_message(cid, m.message_id)
    
    #tresEnRatlla
    elif cid in estatsTresEnRatlla and estatsTresEnRatlla[cid] == JUGANT:
        
        numTirades = numTirades + 1
        if numTirades < 9:
            posicio = m.text

            correcte = comprovacionsNumTresEnRatlla(posicio)

            if not correcte:
                bot.send_message(cid, "Tens d'introduir un número entre 1 i 9.")
            else:
                fi = False
                #comprovem que la posicio estigui lliure
                if fitxesTauler[int(posicio)] == "X" or fitxesTauler[int(posicio)] == "O":
                    posLliure = False
                else:
                    posLliure = True


                #coloquem fitxa
                if posLliure:
                    contestat = True
                    for i in range(len(fitxesTauler)):
                        if fitxesTauler[i] == posicio:
                            fitxesTauler[i] = "X"
                    
                    #cridem mètode per saber si la partida s'ha acabat
                    fi = tresEnRatllaWin("X")
                    if fi:
                        mostrarTauler(cid)
                        estatsTresEnRatlla[cid] = PARTIDA_ACABADA 
                        bot.send_message(cid, "Enhorabonnaaa!!! Has guanyat la partida. ")
                        
                        #reiniciem les variables
                        numTirades = 0
                        fitxesTauler = [" ", "1","2","3","4","5","6","7","8","9","10"] 

                        #sumem el punt a l'usuari
                        cursorObjecte.execute("UPDATE USUARIS SET PUNTUACIO =  PUNTUACIO + 1 where CID = " + str(cid))
                        con.commit()
                    else:
                        #cridem mètode colocar fitxa aleatoria
                        tresEnRatllaMaquina(cid)
                    

                else:
                    missatge = "Posició ocupada!!! Introdueix una nova posició on vols colocar la fitxa: "
                    bot.send_message(cid, missatge)
        else:
            mostrarTauler(cid)
            estatsTresEnRatlla[cid] = PARTIDA_ACABADA 
            missatge = "EMPAT!!!"
            bot.send_message(cid, missatge)
    elif cid in estatsDaus and estatsDaus[cid] == JUGANT:
        
        contestat = True
        numAle = random.randint(1, 6)
        missatge = "Has tret un " + str(numAle)
        bot.send_message(cid, missatge)

        if numAle > numMaquina:
            missatge = "Enhorabonaa!!! Has tingut sort i has guanyat la partida:)" 
            bot.send_message(cid, missatge)
             
             #sumem el punt a l'usuari
            cursorObjecte.execute("UPDATE USUARIS SET PUNTUACIO =  PUNTUACIO + 1 where CID = " + str(cid))
            con.commit()
        elif numAle == numMaquina:
            missatge = "Has tret el mateix número que la màquina, heu empatat" 
            bot.send_message(cid, missatge)
        else:
            missatge = "ohh!! Has tingut mala sort i has perdut la partida :(" 
            bot.send_message(cid, missatge)

        estatsDaus[cid] = PARTIDA_ACABADA



    else:
        bot.send_message(m.chat.id, "No hi ha cap comando aixi, utilitza /ajuda per veure tots els comandos.")


#funció per jugar contra el bot al tres en ratlla
def tresEnRatllaMaquina(cid):
    global numTirades
    global fitxesTauler

 
    posLliure = False
    numAle = random.randint(1, 9)
    numTirades = numTirades + 1
    
    if numTirades < 9:

        while not posLliure:
            if fitxesTauler[numAle] == "X" or fitxesTauler[numAle] == "O":
                numAle = random.randint(1, 9)
            else:
                posLliure = True

        
        fitxesTauler[numAle] = "O"

        #cridem mètode per saber si la partida s'ha acabat
        fi = tresEnRatllaWin("O")
        if fi:
            estatsTresEnRatlla[cid] = PARTIDA_ACABADA 
            mostrarTauler(cid)
            bot.send_message(cid, "Has pertdut!!! ")
            
            #reiniciem les variables
            numTirades = 0
            fitxesTauler = [" ", "1","2","3","4","5","6","7","8","9","10"] 
        else:

            mostrarTauler(cid)
            missatge = "Introdueix la posició on vols colocar la fitxa: "
            bot.send_message(cid, missatge)
    else:
        mostrarTauler(cid)
        estatsTresEnRatlla[cid] = PARTIDA_ACABADA 
        missatge = "EMPAT!!!"
        bot.send_message(cid, missatge)

#funció per comprobar si algu ha guanyat
def tresEnRatllaWin(lletra):
    fi = False

    if fitxesTauler[7] == lletra and fitxesTauler[8] == lletra and fitxesTauler[9] == lletra:
        fi = True
    elif fitxesTauler[4] == lletra and fitxesTauler[5] == lletra and fitxesTauler[6] == lletra:
        fi = True
    elif fitxesTauler[1] == lletra and fitxesTauler[2] == lletra and fitxesTauler[3] == lletra:
        fi = True
    elif fitxesTauler[7] == lletra and fitxesTauler[4] == lletra and fitxesTauler[1] == lletra:
        fi = True
    elif fitxesTauler[8] == lletra and fitxesTauler[5] == lletra and fitxesTauler[2] == lletra:
        fi = True
    elif fitxesTauler[9] == lletra and fitxesTauler[6] == lletra and fitxesTauler[3] == lletra:
        fi = True
    elif fitxesTauler[7] == lletra and fitxesTauler[5] == lletra and fitxesTauler[3] == lletra:
        fi = True
    elif fitxesTauler[1] == lletra and fitxesTauler[5] == lletra and fitxesTauler[9] == lletra:
        fi = True
   
    return fi


#funció per mostrar el tauler
def mostrarTauler(cid):
    missatge = ('-----------\n')
    missatge +=(' ' + fitxesTauler[7] + ' | ' + fitxesTauler[8] + ' | ' + fitxesTauler[9] + '\n')
    missatge +=('-----------\n')
    missatge +=(' ' + fitxesTauler[4] + ' | ' + fitxesTauler[5] + ' | ' + fitxesTauler[6] + '\n')
    missatge +=('-----------\n')
    missatge +=(' ' + fitxesTauler[1] + ' | ' + fitxesTauler[2] + ' | ' + fitxesTauler[3] + '\n')
    missatge +=('-----------\n')
    bot.send_message(cid, missatge)

def comprovacionsNumTresEnRatlla(num):
    correcte = False

    if num.isdigit():
        if int(num) > 0 and int(num) < 10:
            correcte = True
    else:
        correcte = False
    
    return correcte

#funcio per comprobar si el correu es valid
def correuValid(correo):
    expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, correo) is not None


#funcio per comprobar si l'usuari esta registrar
def comprobarRegistre(cid):
    registrat = False

    cursorObjecte.execute('SELECT * FROM USUARIS')
    usuaris = cursorObjecte.fetchall()

    for usuari in usuaris:
        if cid in usuari:
            registrat = True

    return registrat

def contarSegons(cid):
    global contestat
    global numTirades
    global fitxesTauler
    time.sleep(30)

    if not contestat:
        missatge = "S'ha acabat el temps per contestar!!"
        bot.send_message(cid, missatge)
        estatsRegister[cid] = REGISTRAT
        estatsTresEnRatlla[cid] = PARTIDA_ACABADA 
        estatsDaus[cid] = PARTIDA_ACABADA 
        numTirades = 0
        fitxesTauler = [" ", "1","2","3","4","5","6","7","8","9","10"] 



bot.set_update_listener(listener)
bot.polling()
con.close()


