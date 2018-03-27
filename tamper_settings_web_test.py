#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
Summary
========================================================
Tests Camera Tampering Web API Configuration

Web API test:
--------------------------------------
- Sensitivity Range
- Trigger Delay Range
- Settings Persistence
- Restore Defaults
- Invalid Sensitivity
- Invalid Trigger Delay
-------------------
JIRA - FWPRD-370, FWTESTPOOL-534
"""
import pytest
from CameraController.device.camera import Camera

MIN_TAMPER_SENSITIVITY = 1
MAX_TAMPER_SENSITIVITY = 10
DEFAULT_TAMPER_SENSITIVITY = 8

MIN_TAMPER_TRIGGER_DELAY = 1
MAX_TAMPER_TRIGGER_DELAY = 30
DEFAULT_TAMPER_TRIGGER_DELAY = 8

SUCCESS_RESPONSE_CODE = 200


@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.tamper
def test_tamper_settings(camera):
    if camera.cp.props['HardwareId'] in camera.no_video_list:
        camera.logger.info('Camera Tamper is not supported on T%s' % camera.cp.props['HardwareId'])
        pytest.skip('Camera Tamper is not supported on T%s' % camera.cp.props['HardwareId'])
        return 0
    camera.init_camera_log()
    camera.logger.test_start_header('Starting camera tamper settings test')

    tamper_sensitivity_range_test(camera)
    tamper_trigger_delay_range_test(camera)
    tamper_settings_persistence_test(camera)
    tamper_restore_defaults_test(camera)
    # TODO: uncomment when VAL-1482 is fixed
    # tamper_invalid_sensitivity_test(camera)
    # tamper_invalid_trigger_delay_test(camera)

    camera.process_camera_logs('TAMPER WEB API TEST')
    assert camera.logger.get_fail_count() == 0


def tamper_sensitivity_range_test(camera):
    camera.logger.test_start_header("Testing min, max, and valid range of tamper sensitivity.")

    # Test MIN sensitivity
    min_sensitivity = camera.web_service_client.get_tamper_min_sensitivity()
    camera.logger.logresult(min_sensitivity == MIN_TAMPER_SENSITIVITY,
                            "Minimum tamper sensitivity is %s (expected %s)"
                            % (min_sensitivity, MIN_TAMPER_SENSITIVITY))
    # Test MAX sensitivity
    max_sensitivity = camera.web_service_client.get_tamper_max_sensitivity()
    camera.logger.logresult(max_sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Maximum tamper sensitivity is %s (expected %s)"
                            % (max_sensitivity, MAX_TAMPER_SENSITIVITY))

    # Test valid sensitivity range
    for sensitivity_to_set in range(min_sensitivity, max_sensitivity + 1):
        camera.web_service_client.set_tamper_sensitivity(sensitivity_to_set)
        sensitivity = camera.web_service_client.get_tamper_sensitivity()
        camera.logger.logresult(sensitivity == sensitivity_to_set,
                                "Current tamper sensitivity is %s (expected %s)"
                                % (sensitivity, sensitivity_to_set))


def tamper_trigger_delay_range_test(camera):
    camera.logger.test_start_header("Testing min, max, and valid range of tamper trigger delay.")

    # Test MAX sensitivity
    min_trigger_delay = camera.web_service_client.get_tamper_min_trigger_delay()
    camera.logger.logresult(min_trigger_delay == MIN_TAMPER_TRIGGER_DELAY,
                            "Minimum tamper trigger delay is %s (expected %s)"
                            % (min_trigger_delay, MIN_TAMPER_TRIGGER_DELAY))

    # Test MAX trigger delay
    max_trigger_delay = camera.web_service_client.get_tamper_max_trigger_delay()
    camera.logger.logresult(max_trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Maximum tamper trigger delay is %s (expected %s)"
                            % (max_trigger_delay, MAX_TAMPER_TRIGGER_DELAY))

    # Test valid trigger delay range
    for trigger_delay_to_set in range(min_trigger_delay, max_trigger_delay + 1):
        camera.web_service_client.set_tamper_trigger_delay(trigger_delay_to_set)
        trigger_delay = camera.web_service_client.get_tamper_trigger_delay()
        camera.logger.logresult(trigger_delay == trigger_delay_to_set,
                                "Current tamper sensitivity is %s (expected %s)"
                                % (trigger_delay, trigger_delay_to_set))


def tamper_settings_persistence_test(camera):
    camera.logger.test_start_header("Testing settings persistence for tamper sensitivity and trigger delay.")
    camera.logger.info("Setting Non-Default Values")

    # Set MAX sensitivity
    assert MAX_TAMPER_SENSITIVITY != DEFAULT_TAMPER_SENSITIVITY
    camera.web_service_client.set_tamper_sensitivity(MAX_TAMPER_SENSITIVITY)
    sensitivity = camera.web_service_client.get_tamper_sensitivity()
    camera.logger.logresult(sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Current tamper sensitivity is %s (expected %s)"
                            % (sensitivity, MAX_TAMPER_SENSITIVITY))

    # Set MAX trigger delay
    assert MAX_TAMPER_TRIGGER_DELAY != DEFAULT_TAMPER_TRIGGER_DELAY
    camera.web_service_client.set_tamper_trigger_delay(MAX_TAMPER_TRIGGER_DELAY)
    trigger_delay = camera.web_service_client.get_tamper_trigger_delay()
    camera.logger.logresult(trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Current tamper sensitivity is %s (expected %s)"
                            % (trigger_delay, MAX_TAMPER_TRIGGER_DELAY))

    camera.logger.info("Rebooting Camera")
    camera.reboot()

    sensitivity = camera.web_service_client.get_tamper_sensitivity()
    camera.logger.logresult(sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Tamper sensitivity after reboot is: %s (expected %s)"
                            % (sensitivity, MAX_TAMPER_SENSITIVITY))

    trigger_delay = camera.web_service_client.get_tamper_trigger_delay()
    camera.logger.logresult(trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Tamper trigger delay after reboot is: %s (expected %s)"
                            % (trigger_delay, MAX_TAMPER_TRIGGER_DELAY))


def tamper_restore_defaults_test(camera):
    camera.logger.test_start_header("Testing restore to defaults for tamper sensitivity and trigger delay.")
    camera.logger.info("Setting Non-Default Values")

    # Set MAX sensitivity
    assert MAX_TAMPER_SENSITIVITY != DEFAULT_TAMPER_SENSITIVITY
    camera.web_service_client.set_tamper_sensitivity(MAX_TAMPER_SENSITIVITY)
    sensitivity = camera.web_service_client.get_tamper_sensitivity()
    camera.logger.logresult(sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Current tamper sensitivity is %s (expected %s)"
                            % (sensitivity, MAX_TAMPER_SENSITIVITY))

    # Set MAX trigger delay
    assert MAX_TAMPER_TRIGGER_DELAY != DEFAULT_TAMPER_TRIGGER_DELAY
    camera.web_service_client.set_tamper_trigger_delay(MAX_TAMPER_TRIGGER_DELAY)
    trigger_delay = camera.web_service_client.get_tamper_trigger_delay()
    camera.logger.logresult(trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Current tamper sensitivity is %s (expected %s)"
                            % (trigger_delay, MAX_TAMPER_TRIGGER_DELAY))

    camera.logger.info("Restoring factory defaults")
    camera.set_factory_defaults()

    sensitivity = camera.web_service_client.get_tamper_sensitivity()
    camera.logger.logresult(sensitivity == DEFAULT_TAMPER_SENSITIVITY,
                            "Tamper sensitivity after restored factory defaults is: %s (expected %s)"
                            % (sensitivity, DEFAULT_TAMPER_SENSITIVITY))

    trigger_delay = camera.web_service_client.get_tamper_trigger_delay()
    camera.logger.logresult(trigger_delay == DEFAULT_TAMPER_TRIGGER_DELAY,
                            "Tamper trigger delay after restored factory defaults is: %s (expected %s)"
                            % (trigger_delay, DEFAULT_TAMPER_TRIGGER_DELAY))


def tamper_invalid_sensitivity_test(camera):
    camera.logger.test_start_header("Testing invalid sensitivity values")

    # Above MAX sensitivity
    camera.logger.info("Setting above maximum sensitivity value")
    status_code, response_text = camera.web_service_client.set_tamper_sensitivity(MAX_TAMPER_SENSITIVITY + 1)
    camera.logger.logresult(status_code != SUCCESS_RESPONSE_CODE,
                            "Response code from sensitivity above max bound is: %s (not expected: %s)"
                            % (status_code, SUCCESS_RESPONSE_CODE))

    # Below MIN sensitivity
    camera.logger.info("Setting below minimum sensitivity value")
    status_code, response_text = camera.web_service_client.set_tamper_sensitivity(MIN_TAMPER_SENSITIVITY - 1)
    camera.logger.logresult(status_code != SUCCESS_RESPONSE_CODE,
                            "Response code from sensitivity below min bound is: %s (not expected: %s)"
                            % (status_code, SUCCESS_RESPONSE_CODE))

    # Text value
    camera.logger.info("Setting invalid text string as sensitivity")
    status_code, response_text = camera.web_service_client.set_tamper_sensitivity('dummy')
    camera.logger.logresult(status_code != SUCCESS_RESPONSE_CODE,
                            "Response code from invalid text string set as trigger delay is: %s (not expected: %s)"
                            % (status_code, SUCCESS_RESPONSE_CODE))


def tamper_invalid_trigger_delay_test(camera):
    camera.logger.test_start_header("Testing invalid trigger delay values")

    # Above MAX trigger_delay
    camera.logger.info("Setting above maximum trigger delay value")
    status_code, response_text = camera.web_service_client.set_tamper_trigger_delay(MAX_TAMPER_TRIGGER_DELAY + 1)
    camera.logger.logresult(status_code != SUCCESS_RESPONSE_CODE,
                            "Response code from trigger delay above max bound is: %s (not expected: %s)"
                            % (status_code, SUCCESS_RESPONSE_CODE))

    # Below MIN trigger delay
    camera.logger.info("Setting below minimum trigger delay value")
    status_code, response_text = camera.web_service_client.set_tamper_trigger_delay(MIN_TAMPER_TRIGGER_DELAY - 1)
    camera.logger.logresult(status_code != SUCCESS_RESPONSE_CODE,
                            "Response code from trigger delay below min bound is: %s (not expected: %s)"
                            % (status_code, SUCCESS_RESPONSE_CODE))

    # Text value
    camera.logger.info("Setting invalid text string as trigger delay")
    status_code, response_text = camera.web_service_client.set_tamper_trigger_delay('dummy')
    camera.logger.logresult(status_code != SUCCESS_RESPONSE_CODE,
                            "Response code from invalid text string set as trigger delay is: %s (not expected: %s)"
                            % (status_code, SUCCESS_RESPONSE_CODE))


if __name__ == '__main__':
    test_tamper_settings(Camera())
