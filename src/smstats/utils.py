"""
Utility function to handle REST response
"""
from functools import partial, reduce
from json.decoder import JSONDecodeError
from smstats import custom

deref = partial(reduce, lambda dictionary, key: dictionary[key])

def get_resp_param(stage, response, expected_status, key):
    """
    Extract specified parameter from the JSON body of a http response
    """
    # Check if status code match
    if response.status_code != expected_status:
        raise custom.DataGetError(
            f'Error during stage: {stage}. Unexpected reponse status: {response.status_code}')

    # Check if body contains json
    try:
        body = response.json()
    except JSONDecodeError as decode_err:
        raise custom.DataGetError(
            f'Error during stage: {stage}. Could not read json from response') from decode_err

    # Get parameter
    try:
        return deref(key, body)
    except KeyError as key_err:
        raise custom.DataGetError(
            f'Error during stage: {stage}. Parameter {key} not found in received json response') \
        from key_err

def match_resp_param(response, expected_response):
    """
    Check if received response matches expected response
    """
    # Check if status code match
    if response.status_code != expected_response.status:
        return False

    # Check if body contains json
    try:
        body = response.json()
    except JSONDecodeError:
        return False

    # Get parameter
    try:
        value = deref(expected_response.key, body)
    except KeyError:
        return False

    # Match parameter value
    return value == expected_response.value
