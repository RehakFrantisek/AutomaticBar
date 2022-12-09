import json
from cgi import test
import socket
import time
from datetime import datetime, timezone

from PyQt5.QtCore import QThread, QObject
import db.database
#import src.timer

import select
import re

# nastaveni adresy a portu
TCP_IP = '10.20.30.54'
TCP_PORT = 8081
BUFFER_SIZE = 1024
param = []

# nastaveni adresy na odposlech
print("Listening for client...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((TCP_IP, TCP_PORT))
server.listen(1)
rxset = [server]
txset = []
connected = False


class Reader(QThread):

    def __init__(self, parent=None):
        super(Reader, self).__init__(parent)

    def run(self):
        self.reader_connect()

    # filter ID do pole
    def id_tag_split(self, string):
        return re.findall('<TagID>(.*)</TagID>', string)

    def antenna_number(self, string):
        return re.findall('<Antenna>(.)</Antenna>', string)

    # filter datetimu do pole -> nefunkcni
    def disc_time_split(self, string):
        return re.findall('<DiscoveryTime>(.*)</DiscoveryTime>', string)

    # pocet tagu -> k nicemu actual
    def number_of_tags(self, string):
        return len(re.findall('<TagID>(.*)</TagID>', string))

    # ukladani dat do jsonu
    def save_json(self, value1):
        jsonString = json.dumps(str(value1))
        jsonFile = open("../data/data.json", "a")
        jsonFile.write(jsonString + "\n")
        jsonFile.close()

    def reader_connect(self):
        tmp = []
        print('test connect')
        while not connected:
            rxfds, txfds, exfds = select.select(rxset, txset, rxset)
            # pripojeni na adresu
            for sock in rxfds:
                if sock is server:
                    conn, addr = server.accept()
                    conn.setblocking(0)
                    rxset.append(conn)
                    print('Connection from address:', addr)
                else:
                    try:
                        # ziskana data ze socketu
                        data = sock.recv(BUFFER_SIZE)
                        xml_string = data.decode('UTF-8')
                        # print(xml_string)

                        if xml_string != "":
                            self.reader_parse(xml_string)

                    except:
                        # ukonceni spojeni
                        print("Connection closed")
                        param = []
                        rxset.remove(sock)
                        sock.close()
        # print("test reader")

    def reader_parse(self, xml_string):
        value1 = []
        i = 0

        string_id = self.id_tag_split(xml_string)
        antenna = self.antenna_number(xml_string)
        date_time = datetime.now()

        while i < len(string_id):
            tag_id = string_id[i]
            antenna_num = antenna[0]
            db.database.insert_data(tag_id, date_time, antenna_num)
            i += 1
