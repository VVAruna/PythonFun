#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
Summary
========================================================
Tests Camera Tampering ONVIF Analytics Service Rule Configuration

ONVIF API test:
--------------------------------------
Get supported rules
- Min/Max values
- Default values
Get rules
- Enabled
- Sensitivity
- Duration
- Timeout
Modify rules
- Enabled
- Sensitivity
- Duration
- Timeout
Delete rules
References:
-------------------
JIRA - FWPRD-369, FWTESTPOOL-529
"""
import pytest
from CameraController.device.camera import Camera
from suds import WebFault

TAMPER_DEFAULTS = {'Duration': {'Default': 8, 'Max': 30, 'Min': 1},
                   'Sensitivity': {'Default': 8, 'Max': 10, 'Min': 1},
                   'Enabled': {'Default': 1},
                   'Timeout': {'Default': 300, 'Max': 3600, 'Min': 60}
                   }

MIN_TAMPER_SENSITIVITY = 1
MAX_TAMPER_SENSITIVITY = 10
DEFAULT_TAMPER_SENSITIVITY = 8

MIN_TAMPER_TRIGGER_DELAY = 1
MAX_TAMPER_TRIGGER_DELAY = 30
DEFAULT_TAMPER_TRIGGER_DELAY = 8

DEFAULT_TAMPER_ENABLED = 1

MIN_TAMPER_TIMEOUT = 60
MAX_TAMPER_TIMEOUT = 3600
DEFAULT_TAMPER_TIMEOUT = 300

HTTP_OK = 200
SOAP_FAULT = 500


@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.tamper
def test_tamper_settings(camera):
    """
    Performs all Tamper ONVIF API test cases
    :param camera: Camera object
    """
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
    tamper_delete_rule_test(camera)
    # TODO: uncomment when VAL-1482 is fixed
    # tamper_invalid_sensitivity_test(camera)
    # tamper_invalid_trigger_delay_test(camera)

    camera.process_camera_logs('TAMPER WEB API TEST')
    assert camera.logger.get_fail_count() == 0


def get_supported_rule_by_name(camera, rule_name='tavg:CameraTampering'):
    """
    Get supported rule options for a given rule name
    :param camera: Camera object
    :param rule_name: Name of supported rule
    :return: dictionary with Min, Max and Default values for each rule item
    """
    rule_dict = {}

    rule = camera.analytics_client.get_supported_rule_by_name(rule_name)
    for param in rule.Extension.RuleDescriptionExtension.SimpleItemBounds:
        rule_dict.setdefault(param['_Name'], {}).update(
            {'Max': param.Bounds.Max['_Value'], 'Min': param.Bounds.Min['_Value']})
    for param in rule.Extension.RuleDescriptionExtension.SimpleItemDefaultValue:
        rule_dict.setdefault(param['_Name'], {}).update({'Default': param['_Value']})

    return rule_dict


def get_rules(camera):
    """
    Get current settings for a all configured rules
    :param camera: Camera object
    :return: dictionary with rule items and its current values for each rule
    """
    rules_dict = {}

    rules = camera.analytics_client.get_rules()
    for rule in rules:
        for param in rule.Parameters.SimpleItem:
            rules_dict.setdefault(rule['_Name'], {}).update({param['_Name']: param['_Value']})

    return rules_dict


def get_rule_by_name(camera, rule_name='Camera Tampering Rule'):
    """
    Get current rule settings for a given rule name
    :param camera: Camera object
    :param rule_name: Name of supported rule
    :return: dictionary with rule items and its current values
    """
    rules = get_rules(camera)

    if rule_name in rules:
        return rules[rule_name]

    return None


def modify_rule(camera, rule_name, params, cfg_token='ana0'):
    """
    Modify simple key/value parameters in a rule
    Usage: modify_rule("MotionDetector", {"Threshold": 0.5, "Mask": "fffffffff"})
    :param camera:
    :param rule_name: for example 'MotionDetector'
    :param params: dictionary with rule items parameters, for example {"Threshold": 0.5, "Mask": "fffffffff"}
    :param cfg_token: configuration token, dfault - 'ana0'
    :return: HTTP code - HTTP OK (200) if no errors, SERVER ERROR (500) otherwise
    """
    rule = camera.analytics_client.get_rule_by_name(rule_name, cfg_token)

    num_params_set = 0
    for param in rule.Parameters.SimpleItem:
        if param['_Name'] in params.keys():
            num_params_set += 1
            param['_Value'] = params[param['_Name']]

    if num_params_set != len(params):
        camera.cp.logger.warning("Some parameters for rule %s may not have been set!" % rule_name)

    try:
        camera.analytics_client.rule_service.ModifyRules(cfg_token, rule)
        return HTTP_OK
    except WebFault:
        return SOAP_FAULT


def get_tamper_sensitivity(camera):
    return int(get_rule_by_name(camera)['Sensitivity'])


def get_tamper_min_sensitivity(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Sensitivity']['Min'])


def get_tamper_max_sensitivity(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Sensitivity']['Max'])


def get_tamper_default_sensitivity(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Sensitivity']['Default'])


def get_tamper_trigger_delay(camera):
    return int(get_rule_by_name(camera)['Duration'])


def get_tamper_min_trigger_delay(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Duration']['Min'])


def get_tamper_max_trigger_delay(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Duration']['Max'])


def get_tamper_default_trigger_delay(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Duration']['Default'])


def get_tamper_enabled(camera):
    return int(get_rule_by_name(camera)['Enabled'])


def get_tamper_default_enabled(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Enabled']['Default'])


def get_tamper_timeout(camera):
    return int(get_rule_by_name(camera)['Timeout'])


def get_tamper_min_timeout(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Timeout']['Min'])


def get_tamper_max_timeout(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    min_sensitivity = int(tamper_rule['Timeout']['Max'])
    return min_sensitivity


def get_tamper_default_timeout(camera):
    tamper_rule = get_supported_rule_by_name(camera)
    return int(tamper_rule['Timeout']['Default'])


def set_tamper_sensitivity(camera, sensitivity):
    rule = {'Sensitivity': sensitivity}
    return modify_rule(camera, 'Camera Tampering Rule', rule)


def set_tamper_trigger_delay(camera, trigger_delay):
    rule = {'Duration': trigger_delay}
    return modify_rule(camera, 'Camera Tampering Rule', rule)


def set_tamper_enabled(camera, enabled):
    rule = {'Enabled': enabled}
    return modify_rule(camera, 'Camera Tampering Rule', rule)


def set_tamper_timeout(camera, timeout):
    rule = {'Timeout': timeout}
    return modify_rule(camera, 'Camera Tampering Rule', rule)


def tamper_sensitivity_range_test(camera):
    camera.logger.test_start_header("Testing min, max, and valid range of tamper sensitivity.")

    # Test MIN sensitivity
    min_sensitivity = get_tamper_min_sensitivity(camera)
    camera.logger.logresult(min_sensitivity == MIN_TAMPER_SENSITIVITY,
                            "Minimum tamper sensitivity is %s (expected %s)"
                            % (min_sensitivity, MIN_TAMPER_SENSITIVITY))
    # Test MAX sensitivity
    max_sensitivity = get_tamper_max_sensitivity(camera)
    camera.logger.logresult(max_sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Maximum tamper sensitivity is %s (expected %s)"
                            % (max_sensitivity, MAX_TAMPER_SENSITIVITY))

    # Test valid sensitivity range
    for sensitivity_to_set in range(min_sensitivity, max_sensitivity + 1):
        set_tamper_sensitivity(camera, sensitivity_to_set)
        sensitivity = get_tamper_sensitivity(camera)
        camera.logger.logresult(sensitivity == sensitivity_to_set,
                                "Current tamper sensitivity is %s (expected %s)"
                                % (sensitivity, sensitivity_to_set))


def tamper_trigger_delay_range_test(camera):
    camera.logger.test_start_header("Testing min, max, and valid range of tamper trigger delay.")

    # Test MAX sensitivity
    min_trigger_delay = get_tamper_min_trigger_delay(camera)
    camera.logger.logresult(min_trigger_delay == MIN_TAMPER_TRIGGER_DELAY,
                            "Minimum tamper trigger delay is %s (expected %s)"
                            % (min_trigger_delay, MIN_TAMPER_TRIGGER_DELAY))

    # Test MAX trigger delay
    max_trigger_delay = get_tamper_max_trigger_delay(camera)
    camera.logger.logresult(max_trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Maximum tamper trigger delay is %s (expected %s)"
                            % (max_trigger_delay, MAX_TAMPER_TRIGGER_DELAY))

    # Test valid trigger delay range
    for trigger_delay_to_set in range(min_trigger_delay, max_trigger_delay + 1):
        set_tamper_trigger_delay(camera, trigger_delay_to_set)
        trigger_delay = get_tamper_trigger_delay(camera)
        camera.logger.logresult(trigger_delay == trigger_delay_to_set,
                                "Current tamper sensitivity is %s (expected %s)"
                                % (trigger_delay, trigger_delay_to_set))


def tamper_timeout_range_test(camera):
    camera.logger.test_start_header("Testing min, max, and valid range of tamper timeout.")

    # Test MIN timeout
    min_timeout_delay = get_tamper_min_timeout(camera)
    camera.logger.logresult(min_timeout_delay == MIN_TAMPER_TIMEOUT,
                            "Minimum tamper timer is %s (expected %s)"
                            % (min_timeout_delay, MIN_TAMPER_TIMEOUT))

    # Test MAX timeout
    max_timeout_delay = get_tamper_max_timeout(camera)
    camera.logger.logresult(max_timeout_delay == MAX_TAMPER_TIMEOUT,
                            "Maximum tamper timeout is %s (expected %s)"
                            % (max_timeout_delay, MAX_TAMPER_TRIGGER_DELAY))

    # Test valid timeout range
    for timeout_to_set in range(min_timeout_delay, max_timeout_delay + 1):
        set_tamper_timeout(camera, timeout_to_set)
        timeout = get_tamper_trigger_delay(camera)
        camera.logger.logresult(timeout == timeout_to_set,
                                "Current tamper timeout is %s (expected %s)"
                                % (timeout, timeout_to_set))


def tamper_settings_persistence_test(camera):
    camera.logger.test_start_header("Testing settings persistence for tamper sensitivity and trigger delay.")
    camera.logger.info("Setting Non-Default Values")

    # Set MAX sensitivity
    assert MAX_TAMPER_SENSITIVITY != DEFAULT_TAMPER_SENSITIVITY
    set_tamper_sensitivity(camera, MAX_TAMPER_SENSITIVITY)
    sensitivity = get_tamper_sensitivity(camera)
    camera.logger.logresult(sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Current tamper sensitivity is %s (expected %s)"
                            % (sensitivity, MAX_TAMPER_SENSITIVITY))

    # Set MAX trigger delay
    assert MAX_TAMPER_TRIGGER_DELAY != DEFAULT_TAMPER_TRIGGER_DELAY
    set_tamper_trigger_delay(camera, MAX_TAMPER_TRIGGER_DELAY)
    trigger_delay = get_tamper_trigger_delay(camera)
    camera.logger.logresult(trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Current tamper trigger delay is %s (expected %s)"
                            % (trigger_delay, MAX_TAMPER_TRIGGER_DELAY))

    # Set MAX timeout
    assert MAX_TAMPER_TIMEOUT != DEFAULT_TAMPER_TIMEOUT
    set_tamper_timeout(camera, MAX_TAMPER_TIMEOUT)
    timeout = get_tamper_timeout(camera)
    camera.logger.logresult(timeout == MAX_TAMPER_TIMEOUT,
                            "Current tamper timeout is %s (expected %s)"
                            % (timeout, MAX_TAMPER_TIMEOUT))

    camera.logger.info("Rebooting Camera")
    camera.reboot()

    sensitivity = get_tamper_sensitivity(camera)
    camera.logger.logresult(sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Tamper sensitivity after reboot is: %s (expected %s)"
                            % (sensitivity, MAX_TAMPER_SENSITIVITY))

    trigger_delay = get_tamper_trigger_delay(camera)
    camera.logger.logresult(trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Tamper trigger delay after reboot is: %s (expected %s)"
                            % (trigger_delay, MAX_TAMPER_TRIGGER_DELAY))

    timer = get_tamper_timeout(camera)
    camera.logger.logresult(timer == MAX_TAMPER_TIMEOUT,
                            "Tamper timeout after reboot is: %s (expected %s)"
                            % (trigger_delay, MAX_TAMPER_TRIGGER_DELAY))


def tamper_restore_defaults_test(camera):
    camera.logger.test_start_header("Testing restore to defaults for tamper sensitivity and trigger delay.")
    camera.logger.info("Setting Non-Default Values")

    # Set MAX sensitivity
    assert MAX_TAMPER_SENSITIVITY != DEFAULT_TAMPER_SENSITIVITY
    set_tamper_sensitivity(camera, MAX_TAMPER_SENSITIVITY)
    sensitivity = get_tamper_sensitivity(camera)
    camera.logger.logresult(sensitivity == MAX_TAMPER_SENSITIVITY,
                            "Current tamper sensitivity is %s (expected %s)"
                            % (sensitivity, MAX_TAMPER_SENSITIVITY))

    # Set MAX trigger delay
    assert MAX_TAMPER_TRIGGER_DELAY != DEFAULT_TAMPER_TRIGGER_DELAY
    set_tamper_trigger_delay(camera, MAX_TAMPER_TRIGGER_DELAY)
    trigger_delay = get_tamper_trigger_delay(camera)
    camera.logger.logresult(trigger_delay == MAX_TAMPER_TRIGGER_DELAY,
                            "Current tamper sensitivity is %s (expected %s)"
                            % (trigger_delay, MAX_TAMPER_TRIGGER_DELAY))

    # Set MAX timeout
    assert MAX_TAMPER_TIMEOUT != DEFAULT_TAMPER_TIMEOUT
    set_tamper_timeout(camera, MAX_TAMPER_TIMEOUT)
    timeout = get_tamper_timeout(camera)
    camera.logger.logresult(timeout == MAX_TAMPER_TIMEOUT,
                            "Current tamper timeout is %s (expected %s)"
                            % (timeout, MAX_TAMPER_TIMEOUT))

    # Set Enabled
    set_tamper_enabled(camera, 0)
    enabled = get_tamper_enabled(camera)
    camera.logger.logresult(enabled == 0,
                            "Current enabled value is %s (expected %s)"
                            % (enabled, 0))

    camera.logger.info("Restoring factory defaults")
    camera.set_factory_defaults()

    sensitivity = get_tamper_sensitivity(camera)
    camera.logger.logresult(sensitivity == DEFAULT_TAMPER_SENSITIVITY,
                            "Tamper sensitivity after restored factory defaults is: %s (expected %s)"
                            % (sensitivity, DEFAULT_TAMPER_SENSITIVITY))

    trigger_delay = get_tamper_trigger_delay(camera)
    camera.logger.logresult(trigger_delay == DEFAULT_TAMPER_TRIGGER_DELAY,
                            "Tamper trigger delay after restored factory defaults is: %s (expected %s)"
                            % (trigger_delay, DEFAULT_TAMPER_TRIGGER_DELAY))

    timeout = get_tamper_timeout(camera)
    camera.logger.logresult(timeout == DEFAULT_TAMPER_TIMEOUT,
                            "Tamper timeout after restored factory defaults is: %s (expected %s)"
                            % (timeout, DEFAULT_TAMPER_TIMEOUT))

    enabled = get_tamper_default_enabled(camera)
    camera.logger.logresult(enabled == DEFAULT_TAMPER_ENABLED,
                            "Tamper enabled after restored factory defaults is: %s (expected %s)"
                            % (enabled, DEFAULT_TAMPER_ENABLED))


def tamper_invalid_sensitivity_test(camera):
    camera.logger.test_start_header("Testing invalid sensitivity values")

    # Above MAX sensitivity
    camera.logger.info("Setting above maximum sensitivity value")
    response = set_tamper_sensitivity(camera, MAX_TAMPER_SENSITIVITY + 1)
    camera.logger.logresult(response == SOAP_FAULT,
                            "Response from sensitivity above max bound is: %s (expected: %s)"
                            % (response, SOAP_FAULT))

    trigger_delay = get_tamper_sensitivity(camera)
    camera.logger.logresult(trigger_delay != MAX_TAMPER_SENSITIVITY + 1,
                            "Sensitivity should not be %s" % trigger_delay)

    # Below MIN sensitivity
    camera.logger.info("Setting below minimum sensitivity value")
    response = set_tamper_sensitivity(camera, MIN_TAMPER_SENSITIVITY - 1)
    camera.logger.logresult(response == SOAP_FAULT,
                            "Response from sensitivity below min bound is: %s (expected: %s)"
                            % (response, SOAP_FAULT))

    trigger_delay = get_tamper_sensitivity(camera)
    camera.logger.logresult(trigger_delay != MIN_TAMPER_SENSITIVITY - 1,
                            "Sensitivity should not be %s" % trigger_delay)

    # Text value
    camera.logger.info("Setting invalid text string as sensitivity")
    response = set_tamper_sensitivity(camera, 'dummy')
    camera.logger.logresult(response == SOAP_FAULT,
                            "Response from invalid text string set as trigger delay is: %s (expected: %s)"
                            % (response, SOAP_FAULT))


def tamper_invalid_trigger_delay_test(camera):
    camera.logger.test_start_header("Testing invalid trigger delay values")

    # Above MAX trigger_delay
    camera.logger.info("Setting above maximum trigger delay value")
    response = set_tamper_trigger_delay(camera, MAX_TAMPER_TRIGGER_DELAY + 1)
    camera.logger.logresult(response == SOAP_FAULT,
                            "Response from trigger delay above max bound is: %s (expected: %s)"
                            % (response, SOAP_FAULT))

    trigger_delay = get_tamper_trigger_delay(camera)
    camera.logger.logresult(trigger_delay != MAX_TAMPER_TRIGGER_DELAY + 1,
                            "Tamper trigger should not be %s" % trigger_delay)

    # Below MIN trigger delay
    camera.logger.info("Setting below minimum trigger delay value")
    response = set_tamper_trigger_delay(camera, MIN_TAMPER_TRIGGER_DELAY - 1)
    camera.logger.logresult(response == SOAP_FAULT,
                            "Response from trigger delay below min bound is: %s (expected: %s)"
                            % (response, SOAP_FAULT))

    trigger_delay = get_tamper_trigger_delay(camera)
    camera.logger.logresult(trigger_delay != MIN_TAMPER_TRIGGER_DELAY - 1,
                            "Tamper trigger should not be %s" % trigger_delay)

    # Text value
    camera.logger.info("Setting invalid text string as trigger delay")
    response = set_tamper_trigger_delay(camera, 'dummy')
    camera.logger.logresult(response == SOAP_FAULT,
                            "Response from invalid text string set as trigger delay is: %s (expected: %s)"
                            % (response, SOAP_FAULT))


def tamper_delete_rule_test(camera):
    camera.logger.test_start_header("Testing tampering rule deletion")

    try:
        camera.analytics_client.delete_rules('Camera Tampering Rule')
        camera.logger.logresult(False, 'No error when delete Camera Tampering Rule')
    except WebFault as e:
        camera.logger.info(e.message)
        camera.logger.logresult(True, 'Unable to delete Camera Tampering Rule')

    try:
        get_rule_by_name(camera, 'Camera Tampering Rule')
        camera.logger.logresult(True, 'CameraTampering Rule still exists')
    except WebFault as e:
        camera.logger.info(e.message)
        camera.logger.logresult(False, 'Unable to retrieve Camera Tampering Rule settings')


if __name__ == '__main__':
    test_tamper_settings(Camera())
