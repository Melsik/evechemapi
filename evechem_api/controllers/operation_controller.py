import connexion
from evechem_api.models.error import Error
from evechem_api.models.operation import Operation
from evechem_api.models.operation_name import OperationName
from evechem_api.models.key_update import KeyUpdate
from evechem_api.models.key import Key
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

from evechem_api.maps import application_map
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound

from evechem_api.security.definitions import APIKeyControl, APIKey

# used to generate keys
import uuid

keycontrol = APIKeyControl(key_type=APIKey, key_param='api_key')

def is_valid_permission(perm):
    '''Check if `perm` permission is in the list of valid permissions database.
    False if invalid, True if valid.
    '''
    session = application_map.Session()
    qPermission = application_map.Permission

    try:
        q_perm = session.query(qPermission).filter(qPermission.name == perm).one()
        return True
    except NoResultFound:
        return False

@keycontrol.restricted(requires=['master'])
def operation_delete(api_key):
    """
    operation_delete
    Deletes the operation accessed by the given master key.  Note that this invalidates the key and deletes _all_ information under the operation including api keys, towers, and thier configurations. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: None
    """
    session = application_map.Session()

    qOperation = application_map.Operation

    q_operation = session.query(qOperation).filter(qOperation.id == api_key.operation_id).one()
    session.delete(q_operation)
    session.commit()

    return None, 200

@keycontrol.restricted(requires=['master'])
def operation_get(api_key):
    """
    operation_get
    Gets general information about the operation accessed by the given master key. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: Operation
    """
    session = application_map.Session()
    qOperation = application_map.Operation
    qKey = application_map.Key

    q_operation = session.query(qOperation).filter(qOperation.id == api_key.operation_id).one()
    master_key = q_operation.master_key
    

    operation = Operation(
        master_key=master_key.value,
        name=q_operation.name,
        public_name=q_operation.public_name,
        tower_count=len(q_operation.towers),
        sub_key_count=len(q_operation.keys))

    return operation, 200

@keycontrol.restricted(requires=['master'])
def operation_keys_get(api_key):
    """
    operation_keys_get
    Returns &#x60;array&#x60; of operation access sub-keys that exist for this operation. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: List[Key]
    """
    qOperation = application_map.Operation
    qKey = application_map.Key

    session = application_map.Session()
    q_operation = session.query(qOperation).filter(qOperation.id == api_key.operation_id).one()

    keys = [Key(k.name, k.value, k.permission) for k in q_operation.keys]

    return keys,200

@keycontrol.restricted(requires=['master'])
def operation_keys_post(api_key, new_key):
    """
    operation_keys_post
    Creates a new operation access sub-key with the access scopes provided, and then returns the key in the response. 
    :param api_key: Operation Master Access Key
    :type api_key: str
    :param new_key: name/permission info for the new key
    :type new_key: NewKey

    :rtype: Key
    """
    if connexion.request.is_json:
        key = Key.from_dict(connexion.request.get_json())


    session = application_map.Session()
    qKey = application_map.Key

    key.value = uuid.uuid4().hex

    if not is_valid_permission(key.permission):
        error = Error('Bad Request: Permission {} is not valid.'.format(key.permission))
        return error, 400
    elif key.permission == 'master':
        error = Error('Cannot create master key.')
        return error, 400
    else:
        q_newkey = qKey(
            name=key.name,
            value=key.value,
            permission=key.permission,
            operation_id=api_key.operation_id)
        session.add(q_newkey)
        session.commit()

        return key, 200

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
    qKey = application_map.Key
    session = application_map.Session()
    q_key = session.query(qKey).filter(qKey.value == sub_key).filter(qKey.operation_id == api_key.operation_id).one_or_none()
    
    if q_key is None:
        error = Error('Key `{}` not Found'.format(sub_key))
        return error, 404
    elif q_key.permission == 'master':
        error = Error('Cannot delete master key.')
        return error, 400
    else:
        session.delete(q_key)
        session.commit()
        return None, 200

@keycontrol.restricted(requires=['master'])
def operation_keys_sub_key_get(sub_key, api_key):
    """
    operation_keys_sub_key_get
    Gets the permission settings of the given access key. 
    :param sub_key: Operation Access Sub-key
    :type sub_key: str
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: Key
    """
    qKey = application_map.Key
    session = application_map.Session()
    q_key = session.query(qKey).filter(qKey.value == sub_key).filter(qKey.operation_id == api_key.operation_id).one_or_none()
    if q_key is None:
        error = Error('Key `{}` not Found'.format(sub_key))
        return error, 404
    else:
        key = Key(
            name=q_key.name,
            value=q_key.value,
            permission=q_key.permission)
        return key, 200

@keycontrol.restricted(requires=['master'])
def operation_keys_sub_key_patch(sub_key, api_key, key_update):
    """
    operation_keys_sub_key_patch
    Update key_update for the given access sub-key. 
    :param sub_key: Operation Access Sub-key
    :type sub_key: str
    :param api_key: Operation Master Access Key
    :type api_key: str
    :param key_update:
    :type key_update: NewKey

    :rtype: NewKey
    """
    if connexion.request.is_json:
        key_update = Key.from_dict(connexion.request.get_json())

    qKey = application_map.Key
    session = application_map.Session()
   
    if not is_valid_permission(key_update.permission):
        error = Error('Bad Request: Permission {} is not valid.'.format(key_update.permission))
        return error, 400
    elif key_update.permission == 'master':
        error = Error('Cannot set a sub key with permission `master`.')
        return error, 400

    q_key = session.query(qKey).filter(qKey.value == sub_key).filter(qKey.operation_id == api_key.operation_id).one_or_none()
    key_update.value = q_key.value
    if q_key is None:
        error = Error('Key `{}` not Found'.format(sub_key))
        return error, 404

    elif q_key.permission == 'master':
        error = Error('Cannot alter Master Key')
        return error, 400

    else:
        q_key.name = q_key.name if key_update.name is None else key_update.name
        q_key.permission = q_key.permission if key_update.permission is None else key_update.permission
        session.commit()
        return key_update, 200

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
        op_name = OperationName.from_dict(connexion.request.get_json())

    session = application_map.Session()
    qOperation = application_map.Operation

    q_operation = session.query(qOperation).filter(qOperation.id == api_key.operation_id).one()

    q_operation.name = q_operation.name if op_name.name is None else op_name.name
    q_operation.public_name = q_operation.public_name if op_name.public_name is None else op_name.public_name

    session.commit()


    tower_count = 0 # there are no towers yet

    operation = Operation(
        master_key=q_operation.master_key.value,
        name=q_operation.name,
        public_name=q_operation.public_name,
        tower_count=len(q_operation.towers),
        sub_key_count=len(q_operation.keys))

    return operation, 200

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

    name = operation_name.name or "default operation"
    public_name = operation_name.public_name or "default operation - public"

    key_value = uuid.uuid4().hex

    qKey = application_map.Key
    qOperation = application_map.Operation
    session = application_map.Session()

    q_operation = qOperation(
        name=name,
        public_name=public_name)

    q_operation.master_key = qKey(
        value=key_value,
        permission='master',
        name='Master Key')

    operation = Operation(
        master_key=key_value,
        name=name,
        public_name=public_name,
        tower_count=0,
        sub_key_count=1)

    session.add(q_operation)
    session.commit()

    # let sqlite decide what the operation id should be, then make sure they match
    q_operation.master_key.operation_id = q_operation.id
    session.commit()

    return operation, 200
