# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import time
import os
import cv2

from aion.microservice import main_decorator, Options
from aion.kanban import Kanban
from aion.logger import lprint, initialize_logger
from .client.thermo_client import TemperatureClient
from .calc_temperature import Area, get_abnormal_temperature_threshold 
from .enviroment_temperature import get_enviromental_temperature
from .detect_face import detect_face_area


SERVICE_NAME = "detect-abnormal-set-of-temperatures"
DEVICE_NAME = os.environ.get("DEVICE_NAME")
initialize_logger(SERVICE_NAME)
INTERVAL = 1.0
home = os.environ.get('AION_HOME')

@main_decorator(SERVICE_NAME)
def main_with_kanban(opt: Options):
    lprint("start main_with_kanban()")
    # get cache kanban
    conn = opt.get_conn()
    num = opt.get_number()
    kanban = conn.get_one_kanban(SERVICE_NAME, num)

    # get output data path
    data_path = kanban.get_data_path()
    # get previous service list
    service_list = kanban.get_services()

    ######### main function #############

    # output after kanban
    conn.output_kanban(
        result=True,
        connection_key="key",
        output_data_path=data_path,
        process_number=num,
    )


@main_decorator(SERVICE_NAME)
def main_without_kanban(opt: Options):
    lprint("start main_without_kanban()")
    # get cache kanban
    conn = opt.get_conn()
    num = opt.get_number()
    kanban: Kanban = conn.set_kanban(SERVICE_NAME, num)
    data_path = kanban.get_data_path()

    ######### main function #############
    client = TemperatureClient(
                 host='stream-usb-thermo-by-grpc-server-001-srv', port=50051)
    while True:
        env_temp = get_enviromental_temperature()
        temp = client.get_temperature()
        if temp:
            _area = detect_face_area(temp.img)
            if _area[0] and _area[1]:
                lprint(f'detected face area {_area}')
                area = Area(ltop=_area[0], rbottom=_area[1])
            else:
                time.sleep(INTERVAL)
                continue
            threshold = get_abnormal_temperature_threshold(env_temp)
            is_abnormal, ratio = area.detect_abnormal_temperature_over_threshold(temp.table, threshold)
            ave_temp = area.average_temperature(temp.table)
            face_area = [area.left_top[0], area.left_top[1], 
                            area.right_bottom[0], area.right_bottom[1]]
            face_area = [int(x) for x in face_area]
            metadata = {
                "face_area": [face_area[0:2], face_area[2:4]],
                "is_abnormal": is_abnormal,
                "env_temp" : env_temp,
                "threshold": threshold,
                "abnormal_temp_ratio": ratio,
                "average_temp": ave_temp,
                "timestamp": temp.timestamp,
            }
            lprint(metadata)
            # output after kanban
            conn.output_kanban(
                result=True,
                connection_key="key",
                process_number=num,
                metadata=metadata
            )

            cv2.rectangle(temp.img, area.left_top, area.right_bottom, (255, 0, 0), 2)
            cv2.putText(temp.img, f'area temperature: {ave_temp:.1f}', (10, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=2)
            cv2.putText(temp.img, f'abnormal ratio: {ratio:.3f}', (10, 280), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=2)
            cv2.imwrite(os.path.join(data_path, 'face_area.jpg'), temp.img)
        time.sleep(INTERVAL)


@main_decorator(SERVICE_NAME)
def main_with_kanban_itr(opt: Options):
    lprint("start main_with_kanban_itr()")
    # get cache kanban
    conn = opt.get_conn()
    num = int(opt.get_number())
    data_path = os.path.join(home, 'Data', f'{SERVICE_NAME}_{num}')

    ######### main function #############
    client = TemperatureClient(
                host='stream-usb-thermo-by-grpc-server-001-srv', port=50051)

    try:
        for kanban in conn.get_kanban_itr(SERVICE_NAME, num):
            metadata = kanban.get_metadata()
            area_data = metadata.get('area')

            if area_data[0] and area_data[1]:
                lprint(f'face area {area_data}')
                area = Area(ltop=area_data[0], rbottom=area_data[1])
            else:
                area = None
            temp = client.get_temperature()
            if temp and area:
                env_temp = get_enviromental_temperature()
                threshold = get_abnormal_temperature_threshold(env_temp)
                is_abnormal, ratio = area.detect_abnormal_temperature_over_threshold(temp.table, threshold)
                ave_temp = area.average_temperature(temp.table)
                face_area = [area.left_top[0], area.left_top[1], 
                                area.right_bottom[0], area.right_bottom[1]]
                face_area = [int(x) for x in face_area]
                metadata = {
                    "face_area": [face_area[0:2], face_area[2:4]],
                    "is_abnormal": is_abnormal,
                    "env_temp" : env_temp,
                    "threshold": threshold,
                    "abnormal_temp_ratio": ratio,
                    "average_temp": ave_temp,
                    "timestamp": temp.timestamp,
                }
                lprint(metadata)
                conn.output_kanban(
                    result=True,
                    connection_key="key",
                    metadata=metadata,
                    process_number=num,
                )

                cv2.rectangle(temp.img, area.left_top, area.right_bottom, (255, 0, 0), 2)
                cv2.putText(temp.img, f'area temperature: {ave_temp:.1f}', (10, 260),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=2)
                cv2.putText(temp.img, f'abnormal ratio: {ratio:.3f}', (10, 280), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness=2)
                lprint(f'data path: {data_path}')
                cv2.imwrite(os.path.join(data_path, 'face_area.jpg'), temp.img)

    except Exception as e:
        print(str(e))
    finally:
        pass


@main_decorator(SERVICE_NAME)
def send_kanbans_at_highspeed(opt: Options):
    lprint("start send_kanbans_at_highspeed()")
    # get cache kanban
    conn = opt.get_conn()
    num = opt.get_number()
    kanban: Kanban = conn.set_kanban(SERVICE_NAME, num)
    data_path = kanban.get_data_path()
    lprint(DEVICE_NAME)

    index = 0
    while True:
        if index > 20:
            break
        conn.output_kanban(
            result=True,
            connection_key="default",
            output_data_path=data_path,
            metadata={"key": index},
            process_number=num,
            device_name=DEVICE_NAME,
        )
        index = index + 1
        time.sleep(0.5)
