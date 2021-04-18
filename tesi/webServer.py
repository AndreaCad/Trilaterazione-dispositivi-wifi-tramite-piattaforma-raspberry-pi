#!/usr/bin/env python
#WS server
import math
import subprocess
import glob
import os
import asyncio

import websockets
#import pymongo

from pymongo import MongoClient
from datetime import datetime
from datetime import date


# print("debug")
#connessione al db mongodb
client = MongoClient("mongodb+srv://@cluster0.fmw7q.mongodb.net/?retryWrites=true&w=majority")
db = client.progettoreti
collection = db["wifidata"]
# print("debug")


circonferenze = []
punti = []
dev = set()


#classi che identificano punti e circonferenze 
class punto():
    def __init__(self, x,y):
        self.x = x
        self.y = y

class circonferenza():
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r


def get_intersezione(x0, y0, raggio0, x1, y1, raggio1):
    #algoritmo che restituisce, se esistenti, i punti di intersezione tra due circonferenze
    # cerchio 1: (x0, y0), raggio r0
    # cerchio 2: (x1, y1), raggio r1 d=math.sqrt((x1-x0)**2 + ( y1-y0)** 2)
    d = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    #conversione da metri alla grandezza delle coordinate geografiche di google maps
    r0 = raggio0 / 100000
    r1 = raggio1 / 100000
    # non si intersecano
    if d > r0 + r1:
        print("non si intersecano")
        return None
    # un cerchio dentro l altro
    if d < abs(r0-r1):
        print("un cerchio dentro l antro")
        return None
    # cerchi coincidenti
    if d == 0 and r0 == r1:
        print("cerchi coincidenti")
        return None
    else:
        a = (r0**2-r1**2+d**2) / (2 * d)
        h = math.sqrt(r0**2-a ** 2)
        x2 = x0+a * (x1 - x0)/d
        y2 = y0+a * (y1 - y0)/d
        x3 = x2+h * (y1 - y0)/d
        y3 = y2-h * (x1 - x0)/d
        x4 = x2-h * (y1 - y0)/d
        y4 = y2+h * (x1 - x0)/d
        #punti di intersezione
        punto1 = punto(x3, y3)
        punto2 = punto(x4, y4)
        return punto1,punto2

def add_circonferenza(gps, potenzaMedia):
    x = gps.split(",")[0]
    x = gps.split(",")[1]
    r = potenzaMedia


def get_baricentro(lista):
    #algoritmo che calcola il baricentro geometrico di una lista di punti
    x = 0
    y = 0
    for i in range(len(lista)):
        x = x + lista[i].x
    for i in range(len(lista)):
        y = y + lista[i].y
    x1 = x / len(lista)
    y1 = y / len(lista)
    baricentro = punto(x1, y1)
    return x1, y1


def get_potenzaMedia(mac, gps):
    #funzione che fa una ricerca tramite mac e restituisce la potenza media del segnale
    data = collection.find({"mac": mac, "gps": gps})
    results = []
    #ordino la lista e prendo i 4 risultati piu bassi e ne faccio la media
    #questo perche sono i risultati piu accurati
    for x in data:
        results.append(x["segnale"])
    results.sort()
    media = 0
    for x in range(4):
        x = results[x]
        media = media + int(x)

    media = media / 4
    return media

def conversione_metri(pot):
    potenza = abs(pot)
    print(potenza)

    if potenza < 20:
        return 1
    if potenza >= 20 and potenza < 30:
        return 2
    if potenza >= 30 and potenza < 31:
        return 3
    if potenza >= 32 and potenza < 33:
        return 4
    if potenza >= 33 and potenza < 34:
        return 5
    if potenza >= 35 and potenza < 36:
        return 6
    if potenza >= 36 and potenza < 38:
        return 7
    if potenza >= 38 and potenza < 39:
        return 8
    if potenza >= 39 and potenza < 40:
        return 9
    if potenza >= 40 and potenza < 42:
        return 10
    if potenza >= 42 and potenza < 43:
        return 11
    if potenza >= 43 and potenza < 44:
        return 12
    if potenza >= 44 and potenza < 45:
        return 13
    if potenza >= 45 and potenza < 46:
        return 14
    if potenza >= 46 and potenza < 47:
        return 15
    if potenza >= 47 and potenza < 48:
        return 16
    if potenza >= 48 and potenza < 50:
        return 17
    if potenza >= 50 and potenza < 51:
        return 18
    if potenza >= 51 and potenza < 53:
        return 19
    if potenza >= 53 and potenza < 54:
        return 20
    if potenza >= 54 and potenza < 59:
        return 21
    if potenza >= 59 and potenza < 65:
        return 22
    if potenza >= 65 and potenza < 69:
        return 23
    if potenza >= 69 and potenza < 75:
        return 24
    if potenza >= 75 and potenza < 79:
        return 25
    if potenza >= 79 and potenza < 84:
        return 26
    if potenza >= 84 and potenza < 89:
        return 27
    if potenza >= 89:
        return 28

def trilaterazione(mac, data):

    dati = collection.find({"data": data, "mac": mac, "altitudine":"5"})


    datigps = []
    for x in dati:
        print(x["gps"])
        if len(str(x["gps"])) > 30:
            if len(datigps) == 0:
                print("lista vuota")
                datigps.append(x)
            else:
                print("lista non vuota")
                controllo = 1
                for posizione in datigps:
                    print("posizione = " + posizione["gps"])
                    print("x = " + x["gps"])
                    if x["gps"] == posizione["gps"]:
                        print("posizioni uguali")
                        controllo = 0

                if controllo == 1:
                    datigps.append(x)

    print("debug collection")
    print(len(datigps))

    for posizioni in datigps:
        potenzaMedia = get_potenzaMedia(mac,posizioni["gps"])
        print(potenzaMedia)
        distanza = conversione_metri(potenzaMedia)
        print(distanza)
        if posizioni["altitudine"] == "0":
            raggio = distanza
            circonferenze.append(circonferenza(posizioni["gps"].split(",")[0], posizioni["gps"].split(",")[1], raggio))
        else:
            #il raggio e calcolato come base di un triangolo di altezza "altitudine" e ipotenusa "distanza"
            #questo perche si suppone la raccolta dati venga effettuata elevata dal suolo
            raggio = math.sqrt(distanza**2 - int(posizioni["altitudine"])**2)
            circonferenze.append(circonferenza(posizioni["gps"].split(",")[0],posizioni["gps"].split(",")[1],raggio))
    print("debug creazione circo")
    print(len(circonferenze))
    for n in range(len(circonferenze)):
        for m in range(len(circonferenze)):
            if circonferenze[n].x != circonferenze[m].x and circonferenze[n].y != circonferenze[m].y:
                #condizione per no cercare intersezioni tra le stesse circonferenze
                if get_intersezione(float(circonferenze[n].x), float(circonferenze[n].y), float(circonferenze[n].r), float(circonferenze[m].x), float(circonferenze[m].y), float(circonferenze[m].r)) != None:
                    punto1, punto2 = get_intersezione(float(circonferenze[n].x), float(circonferenze[n].y), float(circonferenze[n].r), float(circonferenze[m].x), float(circonferenze[m].y), float(circonferenze[m].r))
                    punti.append(punto1)
                    punti.append(punto2)

    print("debug lista punti")
    print(len(punti))
    return get_baricentro(punti)


class Dispositivo:
    #classe che identifica il dispositivo
    def __init__(self, nome, mac, segnale, data, ora, gps, altitudine):
        self.nome = nome
        self.mac = mac
        self.segnale = segnale
        self.data = data
        self.ora = ora
        self.gps = gps
        self.altitudine = altitudine

    def stampa(self):
        print("nome =", self.nome, "mac =", self.mac, "segnale =", self.segnale, "data =", self.data, "ora =", self.ora, "posizione =", self.gps, "altitudine =", self.altitudine)





def avvio_scan(wlan, tempo):
    #comando per avviare tshark
    subprocess.run(("tshark -I -i " + wlan + " -a duration:" + tempo + " -b files:4 -b filesize:1000 -w /tmp/tshark-temp type mgt subtype probe-req").split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def leggi_scan(wlan, tempo, gps, altitudine,exp):
    avvio_scan(wlan, tempo)

    #ricerca file da leggere (cerca file con numero piu grande finale, ovvero ultimo creato)
    maxFileNumber = -1
    file = ""
    for filename in glob.glob("/tmp/tshark-temp*"):
        fileNumber = int(filename.split("_")[1])
        if fileNumber > maxFileNumber:
            maxFileNumber = fileNumber
            file = filename
    #debug file da leggere
    print(file)
    #lettura file
    cmd = subprocess.Popen(("tshark -r " + file + " -T fields -e wlan.sa_resolved -e wlan.sa -e radiotap.dbm_antsignal").split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #decodifica file
    output = cmd.stdout.read().decode('utf-8')
    #lista dove si salveranno le istanze dispositivi
    dispositivi = []
    #posizione gps rivelazione
    posizione = gps
    today = date.today()
    #data rivelazione
    data = today.strftime("%m/%d/%y")
    now = datetime.now()
    #ora rivelazione
    ora = now.strftime("%H:%M:%S")
    #estrazione dei dati dal file decodificato
    for line in output.splitlines():
        controllo = True
        try:
            nome, mac, power_levels = line.split("\t")
            #aggiungo dispositivi al database
            post = {"mac": mac, "nome": nome, "segnale": power_levels.split(',')[0], "data": data, "ora": ora, "gps": posizione, "altitudine": altitudine,"esperimento": exp}
            collection.insert_one(post)

            #inserimento prima istanza dispositivi stampa
            if len(dispositivi) == 0:
                dispositivi.append(Dispositivo(nome, mac, power_levels.split(',')[0], data, ora, posizione, altitudine))
            #controllo tramite mac per non creare doppioni nella lista
            else:
                for i in range(len(dispositivi)):
                    if mac == dispositivi[i].mac:
                        controllo = False
            #in caso di risultato negativo (mac non presente nella lista) si procede ad inserire il nuovo dispositivo
                if controllo:
                    dispositivi.append(Dispositivo(nome, mac, power_levels.split(',')[0], data, ora, posizione, altitudine))

        except:
            pass
    #eliminazione file creato tramite tshark
    os.remove(file)
    #restituisco la lista dei dispositivi unici rivelati da stampare
    return dispositivi


def get_dev(data):

    print(data)
    dispositivi = collection.find({"data":data})
    for x in dispositivi:
        print(x["mac"])
        dev.add(x["mac"])
    return dev

async def hello(websocket, path):
    async for message in websocket:
        print(f"[From client]: {message}")
        protocol = message.split("-")[0]
        attributes = message.split("-")[1]
        # debug print(attributes)

        if protocol == "$scan":
            #protocollo di avvio scansione
            tempo = message.split("-")[1]
            wlan = message.split("-")[2]
            gps = message.split("-")[3]
            altitudine = message.split("-")[4]
            exp = message.split("-")[5]
            dispositivi = leggi_scan(wlan, tempo, gps, altitudine,exp)
            #debug
            for x in dispositivi:
                print(x.stampa())

            for x in dispositivi:
                await websocket.send("riv$" + x.mac)

        if protocol == "$dev":
            #protocollo di stampa dispositivi rilevati
            print(attributes)

            gg = message.split("-")[3]
            mm = message.split("-")[2]
            aaaa = "21"
            date = str(mm + "/" + gg + "/" + aaaa)
            print(date)

            device = get_dev(date)
            for d in device:
                print(d)
                await websocket.send("dev$" + str(d))

        if protocol == "$track":
            #protocollo di trlaterazione del dispositivo
            mac = message.split("-")[1]


            gg = message.split("-")[4]
            mm = message.split("-")[3]
            aaaa = "21"
            date = str(mm + "/" + gg + "/" + aaaa)
            print(date)

            x , y = trilaterazione(mac, date)
            print(x,",",y)
            await websocket.send("punto$" + str(x) + "---" + str(y))


start_server = websockets.serve(hello, "192.168.1.50", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
