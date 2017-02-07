import connexion
from evechem_api.models.equipment import Equipment
from evechem_api.models.equipment_update import EquipmentUpdate
from evechem_api.models.error import Error
from evechem_api.models.new_equipment import NewEquipment
from evechem_api.models.new_tower import NewTower
from evechem_api.models.process import Process
from evechem_api.models.tower_details import TowerDetails
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def towers_get(api_key):
    """
    towers_get
    Gets summary information for every tower the request is authenticated to see.  This includes &#x60;tower_id&#x60; number, &#x60;type_id&#x60;, fuel status, as well as what the tower is producing at the endpoints of its reaction/mining chains. 
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: List[int]
    """
    return 'do some magic!'


def towers_post(tower, api_key):
    """
    towers_post
    Add new tower. 
    :param tower: New tower information in json format.
    :type tower: dict | bytes
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: None
    """
    if connexion.request.is_json:
        tower = NewTower.from_dict(connexion.request.get_json())
    return 'do some magic!'


def towers_tower_id_delete(tower_id, api_key):
    """
    towers_tower_id_delete
    Delete a specific tower and all its equipment/processes. 
    :param tower_id: Id number of the tower to be deleted.
    :type tower_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'


def towers_tower_id_get(tower_id, api_key):
    """
    towers_tower_id_get
    Gets details for a specific tower with &#x60;type_id&#x60;. 
    :param tower_id: Type of the item that needs fetched.
    :type tower_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: TowerDetails
    """
    return 'do some magic!'


def towers_tower_id_patch(tower_id, api_key, tower_update=None):
    """
    towers_tower_id_patch
    
    :param tower_id: Id number of the tower to be deleted.
    :type tower_id: int
    :param api_key: Operation Access Key
    :type api_key: str
    :param tower_update: Details to update tower with.
    :type tower_update: dict | bytes

    :rtype: TowerDetails
    """
    if connexion.request.is_json:
        tower_update = TowerDetails.from_dict(connexion.request.get_json())
    return 'do some magic!'


def towers_tower_id_processes_get(tower_id, api_key):
    """
    towers_tower_id_processes_get
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: List[Process]
    """
    return 'do some magic!'


def towers_tower_id_processes_post(tower_id, api_key):
    """
    towers_tower_id_processes_post
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: Process
    """
    return 'do some magic!'


def towers_tower_id_processes_process_id_delete(tower_id, process_id, api_key):
    """
    towers_tower_id_processes_process_id_delete
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'


def towers_tower_id_processes_process_id_equipment_equipment_id_delete(tower_id, process_id, equipment_id, api_key):
    """
    towers_tower_id_processes_process_id_equipment_equipment_id_delete
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param equipment_id: Id of equipment that needs fetched.
    :type equipment_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: None
    """
    return 'do some magic!'


def towers_tower_id_processes_process_id_equipment_equipment_id_get(tower_id, process_id, equipment_id, api_key):
    """
    towers_tower_id_processes_process_id_equipment_equipment_id_get
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param equipment_id: Id of equipment that needs fetched.
    :type equipment_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: Equipment
    """
    return 'do some magic!'


def towers_tower_id_processes_process_id_equipment_equipment_id_patch(tower_id, process_id, equipment_id, equipment, api_key):
    """
    towers_tower_id_processes_process_id_equipment_equipment_id_patch
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param equipment_id: Id of equipment that needs fetched.
    :type equipment_id: int
    :param equipment: 
    :type equipment: dict | bytes
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: Equipment
    """
    if connexion.request.is_json:
        equipment = EquipmentUpdate.from_dict(connexion.request.get_json())
    return 'do some magic!'


def towers_tower_id_processes_process_id_equipment_get(tower_id, process_id, api_key):
    """
    towers_tower_id_processes_process_id_equipment_get
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: List[Equipment]
    """
    return 'do some magic!'


def towers_tower_id_processes_process_id_equipment_post(tower_id, process_id, new_equipment, api_key):
    """
    towers_tower_id_processes_process_id_equipment_post
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param new_equipment: 
    :type new_equipment: dict | bytes
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: Equipment
    """
    if connexion.request.is_json:
        new_equipment = NewEquipment.from_dict(connexion.request.get_json())
    return 'do some magic!'


def towers_tower_id_processes_process_id_get(tower_id, process_id, api_key):
    """
    towers_tower_id_processes_process_id_get
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: Process
    """
    return 'do some magic!'
