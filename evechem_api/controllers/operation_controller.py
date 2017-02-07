import connexion
from evechem_api.models.error import Error
from evechem_api.models.operation import Operation
from evechem_api.models.operation_name import OperationName
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

from evechem_api.security.definitions import APIKeyControl, APIKey

keycontrol = APIKeyControl(key_type=APIKey, key_param='api_key')


@keycontrol.restricted(requires=['master'])
def operation_delete(api_key):
    """
    operation_delete
    Deletes the operation accessed by the given master key.  Note that this invalidates the key and deletes _all_ information under the operation including api keys, towers, and thier configurations. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'

@keycontrol.restricted(requires=['master'])
def operation_get(api_key):
    """
    operation_get
    Gets general information about the operation accessed by the given master key. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: Operation
    """
    return 'do some magic!'

@keycontrol.restricted(requires=['master'])
def operation_keys_get(api_key):
    """
    operation_keys_get
    Returns &#x60;array&#x60; of operation access sub-keys that exist for this operation. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: List[str]
    """
    return 'do some magic!'

@keycontrol.restricted(requires=['master'])
def operation_keys_post(api_key):
    """
    operation_keys_post
    Creates a new operation access sub-key with the access scopes provided, and then returns the key in the response. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: str
    """
    return 'do some magic!'

@keycontrol.restricted(requires=['master'])
def operation_keys_sub_key_delete(sub_key, api_key):
    """
    operation_keys_sub_key_delete
    Delete an access sub-key.  The specified key will no longer be valid for accessing any portion of the given operation. 
    :param sub_key: Operation Access Sub-key
    :type sub_key: str
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'

@keycontrol.restricted(requires=['master'])
def operation_keys_sub_key_get(sub_key, api_key):
    """
    operation_keys_sub_key_get
    Gets the permission settings of the given access key. 
    :param sub_key: Operation Access Sub-key
    :type sub_key: str
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: KeyType
    """
    return 'do some magic!'

@keycontrol.restricted(requires=['master'])
def operation_keys_sub_key_patch(sub_key, api_key, key_type):
    """
    operation_keys_sub_key_patch
    Update key_type for the given access sub-key. 
    :param sub_key: Operation Access Sub-key
    :type sub_key: str
    :param api_key: Operation Master Access Key
    :type api_key: str
    :param key_type:
    :type key_type: dict | bytes

    :rtype: KeyType
    """
    if connexion.request.is_json:
        key_type = KeyType.from_dict(connexion.request.get_json())
    return 'do some magic!'

@keycontrol.restricted(requires=['master'])
def operation_patch(api_key, operation_name):
    """
    operation_patch
    Update either private or public name of the operation accessed with the provided master key. 
    :param api_key: Operation Master Access Key
    :type api_key: str
    :param operation_name: Operation Name and Public Name
    :type operation_name: dict | bytes

    :rtype: Operation
    """
    if connexion.request.is_json:
        operation_name = OperationName.from_dict(connexion.request.get_json())
    return 'do some magic!'

def operation_post(operation_name=None):
    """
    operation_post
    Creates a new operation and returns operation details (including the &#x60;master key&#x60;). Optional parameters include the private name and public name of the operation.  These can be changed later. 
    :param operation_name: Operation Name and Public Name
    :type operation_name: dict | bytes

    :rtype: Operation
    """
    if connexion.request.is_json:
        operation_name = OperationName.from_dict(connexion.request.get_json())
    return 'do some magic!'
