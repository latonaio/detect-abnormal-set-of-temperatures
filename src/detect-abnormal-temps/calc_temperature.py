# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import os
import sys

try:
    from aion.logger import lprint
except:
    lprint = print

import numpy as np
import cv2

# CONST PARAMETER
DETECT_ABNORMAL_RATIO = 0.3
ABNORMAL_THRESHOLD_BASE = 38
ABASE = ABNORMAL_THRESHOLD_BASE
ENV_TEMP_XP = [0, 5, 10, 15, 20, 25, 30, 35, 40]
#                             0         5            10         15
ABNORMAL_THRESHOLD_YP =  [ABASE-3.0, ABASE-3.0, ABASE-2.5, ABASE-2.0, 
#                             20        25           30         35        40
                          ABASE-1.5, ABASE-1.0,  ABASE-0.8, ABASE-0.5, ABASE-0]
DEFAULT_ENV_TEMP = 25

class Area():

    MAX_HEIGHT = 288
    MAX_WIDTH = 382

    def __init__(self, ltop, rbottom):
        self.ltop = np.array([int(p) for p in ltop])
        self.rbottom = np.array([int(p) for p in rbottom])

    @property
    def left_top(self):
        return tuple(self.ltop)

    @property
    def right_bottom(self):
        return tuple(self.rbottom)

    @property
    def ltop_w(self):
        return self.ltop[0]

    @property
    def ltop_h(self):
        return self.ltop[1]

    @property
    def rbottom_w(self):
        return self.rbottom[0]

    @property
    def rbottom_h(self):
        return self.rbottom[1]

    def temperatures(self, temps):
        return temps[self.ltop_h:self.rbottom_h, self.ltop_w:self.rbottom_w]

    def average_temperature(self, temps):
        return np.mean(self.temperatures(temps))

    def detect_abnormal_temperature_over_threshold(self, temps, threshold):
        area_temps = self.temperatures(temps)
        pixcel_size = area_temps.shape[0] * area_temps.shape[1]
        if not pixcel_size:
            lprint('[warning] area pixcel size is 0')
            return False, 0
        abnormal_temps_size = np.count_nonzero(area_temps > threshold)
        abnormal_ratio = abnormal_temps_size / pixcel_size 
        if abnormal_ratio > DETECT_ABNORMAL_RATIO:
            return True, abnormal_ratio
        else:
            return False, abnormal_ratio


def get_abnormal_temperature_threshold(env_temp=None):
    if env_temp is not None:
        thresh = np.interp(env_temp, ENV_TEMP_XP, ABNORMAL_THRESHOLD_YP)
    else:
        thresh = np.interp(DEFAULT_ENV_TEMP, ENV_TEMP_XP, ABNORMAL_THRESHOLD_YP)
    return thresh


if __name__ == '__main__':

    if len(sys.argv) > 4:
        l = int(sys.argv[1]), int(sys.argv[2])
        r = int(sys.argv[3]), int(sys.argv[4])
    else:
        l = (50, 50)
        r = (100, 80)
    
    print(l, r)
    
    index = 4
    img = cv2.imread(f'/home/latona/odin/Runtime/optris_try/python/data/thermal_{index}.png', 1)
    temps = np.loadtxt(f'/home/latona/odin/Runtime/optris_try/python/data/thermal_{index}.csv', delimiter=',')
    dtemp = temps.reshape(288, 382, 1)[:, :, ::-1]
    dtemp = dtemp / 10. - 100

    area = Area(ltop=l, rbottom=r)

    result = area.detect_abnormal_temperature_over_threshold(dtemp, 30)
    print(f'detect_abnormal_temp_area: {result}')

    area_temp = area.average_temperature(dtemp)
    print(f'average temp in area: {area_temp}')
    img = cv2.rectangle(img, area.left_top, area.right_bottom, (0, 255, 0), 2)
    img = cv2.putText(img, f'area temp:{area_temp:.1f}', area.left_top, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), thickness=2)
    img = cv2.putText(img, f'temperature thresh: {30.0}', (10, 260), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=2)
    img = cv2.putText(img, f'abnormal ratio: {ratio}', (10, 280), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=2)

    cv2.imshow('image', img)
    cv2.waitKey(0)
