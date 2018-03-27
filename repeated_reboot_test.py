#!/usr/bin/env python
"""
PTZ VAL Status Test (T202-862, T202-894, T202-985)
-------------------------------------------------------------

Steps:
-------
1) Set random Pan/Tilt/Zoom position
2) Set as a Home position
3) Check VAL status
4) Reboot camera
5) Check VAL status
"""
import time
from random import randrange
from CameraController.device.camera import Camera

MOVE_TIMEOUT_SECONDS = 10
POLL_TIME = 0.5
MOVE_SPEED = 0.8
PAN_TILT_STEPS = 99840
ZOOM_STEPS = 16384


def test_repeated_reboot_test(camera):
    camera.logger.info('-------------------------------')
    camera.logger.info('Starting Repeated Reboot Tests')
    camera.logger.info('-------------------------------')

    repeats = 1
    if 'repeat' in camera.arguments:
        repeats = camera.arguments['repeat']

    repeated_reboot_test(camera, total_repeat=repeats)

    assert camera.logger.get_fail_count() == 0


def repeated_reboot_test(camera, total_repeat=10000000):
    if 'G-' in camera.cp.props['Model']:
        stream_message = 'CreateStream'
    else:
        stream_message = 'PlayStream'

    camera.avigilon_client.goto_ptz_home(camera)
    camera.ptz_client.wait_for_move_finish(timeout=10, poll_time=0.5)
    get_ptz_position(camera)
    check_val_status(camera, 'NOT PAUSED')

    for total_repeat_count in range(1, total_repeat + 1):
        camera.logger.info("~~~~~~~~~~~ Running %d of %d  iteration of repeated Reboot ~~~~~~~~~~~~" %
                           (total_repeat_count, total_repeat))

        cl = camera.get_camera_log()

        set_random_ptz_position(camera)
        get_ptz_position(camera)
        camera.logger.info("Set current position as Home")
        # camera.ptz_client.create_preset('preset000')
        camera.avigilon_client.set_ptz_home(camera)

        camera.reboot()
        camera.logger.logresult(cl.wait_for_logmessage(stream_message, timeout=30), 'Camera logged "%s ... "' %
                                stream_message)
        time.sleep(10)
        camera.ptz_client.wait_for_move_finish(timeout=10, poll_time=0.5)
        get_ptz_position(camera)
        check_val_status(camera, 'NOT PAUSED')

        camera.process_camera_logs('REPEATED REBOOT TEST')

        time.sleep(camera.arguments['wait'])


def get_ptz_position(camera):
    """
    get and log ptz position
    """
    pos = camera.ptz_client.get_status().Position
    camera.logger.info("Current Pan: %f, Tilt: %f, Zoom: %f" % (pos.PanTilt._x, pos.PanTilt._y, pos.Zoom._x))
    return pos.PanTilt._x, pos.PanTilt._y, pos.Zoom._x


def check_val_status(camera, paused):
    """
    check val status after delay
    """
    time.sleep(5)
    val_status = camera.avigilon_client.get_val_status()
    camera.logger.logresult(val_status == paused, 'Verify VAL is %s' % paused)
    return val_status


def set_random_ptz_position(camera):
    """
    move to random ptz position
    """
    # random_pan, random_tilt, random_zoom = random(), random(), random()
    random_pan, random_tilt, random_zoom = randrange(PAN_TILT_STEPS) / float(PAN_TILT_STEPS), \
                                           randrange(PAN_TILT_STEPS) / float(PAN_TILT_STEPS), \
                                           randrange(ZOOM_STEPS) / float(ZOOM_STEPS)
    camera.logger.info("Moving to random Pan: %f, Tilt: %f, Zoom: %f" % (random_pan, random_tilt, random_zoom))
    camera.ptz_client.set_position_absolute(random_pan, random_tilt, speed=MOVE_SPEED)

    # wait for move to end
    move_completed = camera.ptz_client.wait_for_move_finish(timeout=MOVE_TIMEOUT_SECONDS, poll_time=POLL_TIME)
    if not move_completed:
        camera.logger.warning("wait_for_move_finish timed out, operation may not have completed!")

    camera.ptz_client.set_zoom_absolute(random_zoom, speed=MOVE_SPEED)
    camera.ptz_client.monitor_zoom_status()
    return random_pan, random_tilt, random_zoom


if __name__ == '__main__':
    test_repeated_reboot_test(Camera())
