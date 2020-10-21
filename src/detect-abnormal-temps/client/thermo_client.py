# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

from concurrent import futures
import time
import cv2
import grpc
import base64
import numpy as np
import sys
from pathlib import Path

from . import thermo_pb2
from . import thermo_pb2_grpc


WIDTH = 382
HEIGHT = 288


class Temperature():
    def __init__(self, img, temperatures, timestamp=None):
        self.img = img
        self.table = temperatures / 10. - 100
        self.timestamp = timestamp


# NOTE: NO USE NOW
class TemperatureDecoder():

    def calc_temp(self, temps):
        return temps / 10. - 100

    def decode(self, image, temperatures, timestamp=None):
        img_64d = base64.b64decode(image)
        img_Buf = np.frombuffer(img_64d, dtype=np.uint8)
        dst_img = cv2.imdecode(img_Buf, cv2.IMREAD_COLOR)
        temp_64d = base64.b64decode(temperatures)
        dtemps = np.frombuffer(temp_64d, dtype=np.uint16)
        dst_temps = temperatures.reshape(HEIGHT, WIDTH, 1)[:, :, ::-1]
        return Temperature(dst_img, calc_temp(dst_temps), timestamp)


class TemperatureClient():

    def __init__(self, host='127.0.0.1', port=50051):
        self.host = host
        self.port = port

    def get_temperature(self):
        address = f'{self.host}:{self.port}'
        print(f'access to server:{address}')
        with grpc.insecure_channel(address) as channel:
            stub = thermo_pb2_grpc.TemperatureServerStub(channel)
            try:
                res = stub.getTemperature(thermo_pb2.TemperatureRequest())
                t1 = time.time()
                for r in res:
                    bimg_64d = base64.b64decode(r.image)
                    btemp_64d = base64.b64decode(r.temperatures)
                    timestamp = r.timestamp

                    dimg = np.frombuffer(bimg_64d, dtype=np.uint8)
                    dst_img = cv2.imdecode(dimg, cv2.IMREAD_COLOR)
                    d_temperatures = np.frombuffer(btemp_64d, dtype=np.uint16)
                    d_temperatures = d_temperatures.reshape(
                                            HEIGHT, WIDTH, 1)[:, :, ::-1]
                    t = Temperature(dst_img, d_temperatures, timestamp)
                    print('recieve size: ', t.img.shape, t.table.shape)
                    t2 = time.time()
                    print(f'recieve time: {t2 - t1}')
                    t1 = t2

            except grpc.RpcError as e:
                print(e.details())
                return None
        return t

if __name__ == '__main__':
    with grpc.insecure_channel('127.0.0.1:50051') as channel:
        stub = thermo_pb2_grpc.TemperatureServerStub(channel)
        try:
            res = stub.getTemperature(thermo_pb2.TemperatureRequest())
            for r in res:
                bimg_64d = base64.b64decode(r.image)
                btemp_64d = base64.b64decode(r.temperatures)
                timestamp = r.timestamp
                dimg_Buf = np.frombuffer(bimg_64d, dtype=np.uint8)
                dst_img = cv2.imdecode(dimg_Buf, cv2.IMREAD_COLOR)
                d_temperatures = np.frombuffer(btemp_64d, dtype=np.uint16)
                print((dst_img.shape))
                print(d_temperatures.shape)
                print(timestamp)
        except grpc.RpcError as e:
            print(e.details())
        print("finish client")
