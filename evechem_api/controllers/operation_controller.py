import connexion
from evechem_api.models.error import Error
from evechem_api.models.operation import Operation
from evechem_api.models.operation_name import OperationName
from evechem_api.models.key_type import KeyType
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

from evechem_api.maps import application_map
from sqlalchemy.orm import aliased

from evechem_api.security.definitions import APIKeyControl, APIKey

# used to generate keys
import uuid

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
    session = application_map.Session()

    session.query(application_map.Key).filter(application_map.Key.operation_id == api_key.operation_id).delete()
    session.query(application_map.Operation).filter(application_map.Operation.operation_id == api_key.operation_id).delete()

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
    qPermission = application_map.Permission

    master_level = session.query(qPermission).filter(qPermission.name == 'master').one().level

    q_operation = session.query(qOperation).filter(qOperation.operation_id == api_key.operation_id).one()
    q_op_keys = session.query(qKey).filter(qKey.operation_id == api_key.operation_id)

    master_key = q_op_keys.filter(qKey.permission_level == master_level).one()
    key_count = q_op_keys.count() - 1

    tower_count = 0 # tower backend not implemented yet

    operation = Operation(
        master_key=master_key.key,
        name=q_operation.name,
        public_name=q_operation.public_name,
        tower_count=tower_count,
        sub_key_count=key_count)

    return operation, 200

@keycontrol.restricted(requires=['master'])
def operation_keys_get(api_key):
    """
    operation_keys_get
    Returns &#x60;array&#x60; of operation access sub-keys that exist for this operation. 
    :param api_key: Operation Master Access Key
    :type api_key: str

    :rtype: List[str]
    """
    Key = aliased(application_map.Key)
    Permission = aliased(application_map.Permission)

    session = application_map.Session()
    q = session.query(Key).join(Permission).filter(Permission.name != 'master').filter(Key.operation_id == api_key.operation_id)
    q_keys = q.all()

    keys = [k.key for k in q_keys]

    return keys,200

@keycontrol.restricted(requires=['master'])
def operation_keys_post(api_key, key_type):
    """
    operation_keys_post
    Creates a new operation access sub-key with the access scopes provided, and then returns the key in the response. 
    :param api_key: Operation Master Access Key
    :type api_key: str
    :param key_type: KeyType level of new key
    :type key_type: KeyType

    :rtype: str
    """
    if connexion.request.is_json:
        key_type = KeyType.from_dict(connexion.request.get_json())


    session = application_map.Session()

    Key = aliased(application_map.Key)
    Permission = aliased(application_map.Permission)

    key_value = uuid.uuid4().hex
    key_level = session.query(Permission).filter(Permission.name == key_type.permission).one_or_none().level

    if key_level is None:
        error = Error('Bad Request: Permission {} is not valid.'.format(key_type.permission))
        return error, 400
    new_key = application_map.Key(
        key=key_value,
        permission_level=key_level,
        operation_id=api_key.operation_id)
    session.add(new_key)
    session.commit()
    return key_value, 200

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
    Key = application_map.Key
    session = application_map.Session()
    q = session.query(Key).filter(Key.key == sub_key).filter(Key.operation_id == api_key.operation_id)
    q_key = q.one_or_none()
    if q_key is None:
        error = Error('API Key not Found')
        return error, 404
    elif q_key.permission.name == 'master':
        error = Error('Bad Request: Cannot delete master key.')
        return error, 400
    else:
        q.delete()
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

    :rtype: permission
    """
    Key = application_map.Key
    session = application_map.Session()
    q_key = session.query(Key).filter(Key.key == sub_key).filter(Key.operation_id == api_key.operation_id).one_or_none()
    if q_key is None:
        error = Error('API Key not Found')
        return error, 404
    else:
        permission = {'permission':q_key.permission.name}
        return permission, 200

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
    :type key_type: KeyType

    :rtype: KeyType
    """
    if connexion.request.is_json:
        key_type = KeyType.from_dict(connexion.request.get_json())

    Key = application_map.Key
    Permission = application_map.Permission

    session = application_map.Session()
    permission = session.query(Permission).filter(Permission.name == key_type.permission).filter(Permission.name != 'master').one_or_none()

    if permission is None:
        error = Error('Bad Request: Permission {} is not valid.'.format(key_type.permission))
        return error, 400

    q_key = session.query(Key).filter(Key.key == sub_key).filter(Key.operation_id == api_key.operation_id).one_or_none()
    if q_key is None:
        error = Error('API Key not Found')
        return error, 404
    elif q_key.permission.name == 'master':
        error = Error('Bad Request: Cannot alter Master Key')
        return error, 400
    else:
        q_key.permission_level = permission.level

    session.commit()
    return key_type, 200

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
    qPermission = application_map.Permission
    qKey = application_map.Key

    q_operation = session.query(qOperation).filter(qOperation.operation_id == api_key.operation_id).one()

    if op_name:
        q_operation.name = op_name.name if op_name.name else q_operation.name
        q_operation.public_name = op_name.public_name if op_name.public_name else q_operation.public_name

    session.commit()

    q_op_keys = session.query(qKey).filter(qKey.operation_id == api_key.operation_id)
    master_level = session.query(qPermission).filter(qPermission.name == 'master').one().level
    master_key = q_op_keys.filter(qKey.permission_level == master_level).one()
    key_count = q_op_keys.count() - 1

    tower_count = 0 # tower backend not implemented yet

    operation = Operation(
        master_key=master_key.key,
        name=q_operation.name,
        public_name=q_operation.public_name,
        tower_count=tower_count,
        sub_key_count=key_count)

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

    if operation_name:
        name = operation_name.name
        public_name = operation_name.public_name
    else:
        name = "Operation"
        public_name = "Operation Public"

    key_value = uuid.uuid4().hex

    session = application_map.Session()
    qKey = application_map.Key
    qOperation = application_map.Operation
    qPermission = application_map.Permission

    key_level = session.query(qPermission).filter(qPermission.name == 'master').one_or_none().level

    q_master_key = qKey(
        key=key_value,
        permission_level=key_level)

    q_operation = qOperation(
        name=name,
        public_name=public_name)

    operation = Operation(
        master_key=key_value,
        name=name,
        public_name=public_name)

    session.add_all([q_master_key, q_operation])
    session.commit()

    # let sqlite decide what the operation id should be, then make sure they match
    q_master_key.operation_id = q_operation.operation_id
    session.commit()

    return operation, 200
