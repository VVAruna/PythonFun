#!/usr/bin/env python
"""
Print PTZ coordinates and VAL status
"""
import time
from random import random
from CameraController.device.camera import Camera
from CameraController.utils.utils import isclose


def get_ptz_position(camera):
    """
    get and log ptz position
    """
    pos = camera.ptz_client.get_status().Position
    camera.logger.info("Current Pan: %f, Tilt: %f, Zoom: %f" % (pos.PanTilt._x, pos.PanTilt._y, pos.Zoom._x))
    return pos.PanTilt._x, pos.PanTilt._y, pos.Zoom._x


def get_val_status(camera):
    """
    check val status after delay
    """
    val_status = camera.avigilon_client.get_val_status()
    camera.logger.info('VAL status is %s' % val_status)
    return val_status


if __name__ == '__main__':
    camera = Camera()
    while True:
        get_ptz_position(camera)
        get_val_status(camera)
        time.sleep(2)
