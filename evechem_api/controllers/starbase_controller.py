import connexion
from evechem_api.models.equipment import Equipment
from evechem_api.models.equipment_update import EquipmentUpdate
from evechem_api.models.error import Error
from evechem_api.models.new_equipment import NewEquipment
from evechem_api.models.link import Link
from evechem_api.models.new_tower import NewTower
from evechem_api.models.process import Process
from evechem_api.models.tower_details import TowerDetails
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm.exc import NoResultFound

import random
import time

from evechem_api.security.definitions import APIKeyControl, APIKey
keycontrol = APIKeyControl(key_type=APIKey, key_param='api_key')

from evechem_api.maps import application_map
from evechem_api.maps import info_map

# required access level presets
AT_LEAST_AUDITOR = ['master','director','manager', 'auditor']
AT_LEAST_MANAGER = ['master','director','manager']
AT_LEAST_DIRECTOR = ['master','director']
MASTER = ['master']


class EquipmentNotFound(Exception):
    pass

class ResourceNotFound(Exception):
    pass

class InvalidLinkMaterial(Exception):
    pass

class ProcessTree(object):

    def __init__(self, equipment):
        self.equipment = equipment

    def top_level(self):
        top_level_equipment = [node for node in self.equipment if len(node.parents) == 0]
        return top_level_equipment

    def production_endpoints(self):
        endpoints = [n.id for n in self.top_level() if self._in_production_branch(n)]
        return endpoints


    def _in_production_branch(self, node):
        if type(node) is StorageNode:
            for child in node.children:
                if type(child) is ProductionNode:
                    return True
                elif type(child) is StorageNode:
                    return self._in_production_branch(child)

            return False

    @classmethod
    def fromId(cls, process_id):
        qEquipmentInfo = info_map.Equipment
        info_session = info_map.Session()
        storage_types = [e.type for e in info_session.query(qEquipmentInfo).filter(qEquipmentInfo.group_id==404).all()]

        nodes = {}

        qProcess = application_map.Process
        session = application_map.Session()

        q_process = session.query(qProcess).filter(qProcess.id==process_id).one()
        for q_equipment in q_process.equipment:
            if q_equipment.type in storage_types:
                Node = StorageNode
            else:
                Node = ProductionNode

            nodes[q_equipment.id] = Node(
                id=q_equipment.id,
                children=[l.source for l in q_equipment.inputs],
                parents=[l.target for l in q_equipment.outputs])

        # properly link nodes
        for node_id in nodes:
            node = nodes[node_id]
            node.children = [nodes[id] for id in node.children]
            node.parents = [nodes[id] for id in node.parents]


        return cls(equipment=[nodes[id] for id in nodes])

class ProcessNode(object):
    def __init__(self, id, children=[], parents=[]):
        self.id = id
        self.children = children
        self.parents = parents

class ProductionNode(ProcessNode):
    pass

class StorageNode(ProcessNode):
    pass

def make_link(source_id, target_id, material_id):
    '''make_link(source_id, target_id, material_id)

    creates a link entry with the given parameters.

    if either the source or target equipment does not produce/consume 
    the material_id, returns a InvalidLinkMaterial exception.  If a material
    link slot is already occupied on either end of the equipment, the old link
    is replaced with the new one.  This happens silently.
    '''
    qLink = application_map.Link
    qEquipment = application_map.Equipment
    session = application_map.Session()


    source_linkable = available_links(source_id)
    target_linkable = available_links(target_id, outputs=False)

    if material_id in source_linkable and material_id in target_linkable:
        # see if this material has been linked to/from either source or target equipment
        q_link = session.query(qLink).filter(
            and_(
                qLink.resource==material_id,
                or_(
                    qLink.source==source_id,
                    qLink.target==target_id))).one_or_none()
        if q_link is None:
            # link does not exist, make a new one
            q_link = qLink(
                source=source_id,
                target=target_id,
                resource=material_id)
            session.add(q_link)
        else:
            # the material was linked already, just modify the old link
            q_link.source = source_id
            q_link.target = target_id

        session.commit()

    else:
        raise InvalidLinkMaterial('Not a valid Link Material (must be both an output at source and input at target).')

def available_links(equipment_id, outputs=True):
    qEquipment = application_map.Equipment
    qEquipmentInfo = info_map.Equipment
    qMaterial = info_map.Material
    qReaction = info_map.Reaction

    session = application_map.Session()
    info_session = info_map.Session()

    q_equipment = session.query(qEquipment).filter(qEquipment.id==equipment_id).one()

    # special handle for mining arrays (unlike silos they have no inputs)
    mining_equipment_type = info_session.query(qEquipmentInfo).filter(qEquipmentInfo.name=='Moon Harvesting Array')
    if q_equipment.type == mining_equipment_type:
        if outputs:
            return [q_equipment.resource]
        else:
            return []

    resource = q_equipment.resource
    if resource is None:
        return []
    else:
        q_reaction = info_session.query(qReaction).filter(qReaction.type==resource).one_or_none()
        if q_reaction is None:
            q_material = info_session.query(qMaterial).filter(qMaterial.type==resource).one()
            return [resource]
        else:
            if outputs:
                return [m.material_id for m in q_reaction.outputs]
            else:
                return [m.material_id for m in q_reaction.inputs]

def resource_allowed(equipment_type, resource_type):
    qEquipment = info_map.Equipment
    qGroup = info_map.Group
    qMaterial = info_map.Material
    qReaction = info_map.Reaction

    session = info_map.Session()

    
    try:
        q_equipment = session.query(qEquipment).filter(qEquipment.type==equipment_type).one()
    except NoResultFound:
        raise EquipmentNotFound('Equipment `{}` not valid.'.format(equipment_type))

    q_material = session.query(qMaterial).filter(qMaterial.type==resource_type).one_or_none()
    q_reaction = session.query(qReaction).filter(qReaction.type==resource_type).one_or_none()

    if q_material is None:
        if q_reaction is None:
            raise ResourceNotFound('Resource `{}` not valid.'.format(resource_type))
        else:
            q_resource = q_reaction
    else:
        q_resource = q_material

    if q_equipment.groups.filter(qGroup.group_id==q_resource.group_id).one_or_none() is None:
        return False
    else:
        return True

@keycontrol.restricted(requires=AT_LEAST_AUDITOR)
def towers_get(api_key):
    """
    towers_get
    Gets summary information for every tower the request is authenticated to see.  This includes &#x60;tower_id&#x60; number, &#x60;type_id&#x60;, fuel status, as well as what the tower is producing at the endpoints of its reaction/mining chains. 
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: List[int]
    """
    qOperation = application_map.Operation
    session = application_map.Session()
    q_operation = session.query(qOperation).filter(qOperation.id == api_key.operation_id).one()

    return [t.id for t in q_operation.towers], 200

@keycontrol.restricted(requires=AT_LEAST_DIRECTOR)
def towers_post(tower_details, api_key):
    """
    towers_post
    Add new tower. 
    :param tower_details: New tower information in json format.
    :type tower_details: dict | bytes
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: TowerDetails
    """
    if connexion.request.is_json:
        tower_details = TowerDetails.from_dict(connexion.request.get_json())

    if tower_details.fuel_last_update is None:
        tower_details.fuel_last_update = int(time.time())        

    qTower = application_map.Tower
    session = application_map.Session()
    newTower = qTower(
        op_id=api_key.operation_id,
        type=tower_details.type,
        name=tower_details.name,
        system=tower_details.system,
        planet=tower_details.planet,
        moon=tower_details.moon,
        cycles_at=tower_details.cycles_at,
        stront_count=tower_details.stront_count,
        fuel_count=tower_details.fuel_count,
        fuel_last_update=tower_details.fuel_last_update,
        online=tower_details.online,
        sov=tower_details.sov)

    session.add(newTower)
    session.commit()
    newTower.id += random.randint(0,999) # add some uncertainty so that id is not directly tower count
    tower_details.id = newTower.id

    session.commit()

    return tower_details, 200

@keycontrol.restricted(requires=AT_LEAST_AUDITOR)
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

    qTower = application_map.Tower
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404
    else:
        tower_details = TowerDetails(
            id=q_tower.id,
            type=q_tower.type,
            system=q_tower.system,
            planet=q_tower.planet,
            moon=q_tower.moon,
            name=q_tower.name,
            cycles_at=q_tower.cycles_at,
            stront_count=q_tower.stront_count,
            fuel_count=q_tower.fuel_count,
            fuel_last_update=q_tower.fuel_last_update,
            online=q_tower.online,
            sov=q_tower.sov,
            processes=[p.id for p in q_tower.processes])

        return tower_details, 200

@keycontrol.restricted(requires=AT_LEAST_DIRECTOR)
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
    qTower = application_map.Tower
    session = application_map.Session()

    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404
    else:
        session.delete(q_tower)
        session.commit()
    return None, 200

@keycontrol.restricted(requires=AT_LEAST_MANAGER)
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

    qTower = application_map.Tower
    session = application_map.Session()

    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404
    else:
        if tower_update.type is not None:
            q_tower.type = tower_update.type
        if tower_update.system is not None:
            q_tower.system = tower_update.system
        if tower_update.planet is not None:
            q_tower.planet = tower_update.planet
        if tower_update.moon is not None:
            q_tower.moon = tower_update.moon
        if tower_update.cycles_at is not None:
            q_tower.cycles_at = tower_update.cycles_at
        if tower_update.fuel_count is not None:
            q_tower.fuel_count = tower_update.fuel_count
        if tower_update.fuel_last_update is not None:
            q_tower.fuel_last_update = tower_update.fuel_last_update
        if tower_update.online is not None:
            q_tower.online = tower_update.online
        if tower_update.sov is not None:
            q_tower.sov = tower_update.sov
        if tower_update.name is not None:
            q_tower.name = tower_update.name
        if tower_update.stront_count is not None:
            q_tower.stront_count = tower_update.stront_count

        tower_details = TowerDetails(
            id=q_tower.id,
            type=q_tower.type,
            system=q_tower.system,
            planet=q_tower.planet,
            moon=q_tower.moon,
            name=q_tower.name,
            cycles_at=q_tower.cycles_at,
            stront_count=q_tower.stront_count,
            fuel_count=q_tower.fuel_count,
            fuel_last_update=q_tower.fuel_last_update,
            online=q_tower.online,
            sov=q_tower.sov,
            processes=[])

        session.commit()

        return tower_details, 200


@keycontrol.restricted(requires=AT_LEAST_AUDITOR)
def towers_tower_id_processes_get(tower_id, api_key):
    """
    towers_tower_id_processes_get
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: List[Process]
    """
    qProcess = application_map.Process
    qTower = application_map.Tower
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    processes = []
    for q_process in q_tower.processes:
        processes.append(Process(
            id=q_process.id,
            equipment = [e.id for e in q_process.equipment],
            final_outputs=[]))

    return processes, 200

@keycontrol.restricted(requires=AT_LEAST_DIRECTOR)
def towers_tower_id_processes_post(tower_id, api_key):
    """
    towers_tower_id_processes_post
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: Process
    """
    qProcess = application_map.Process
    qTower = application_map.Tower
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    q_process = qProcess()
    q_tower.processes.append(q_process)
    session.commit()
    q_process.id += random.randint(0,99) # add some uncertainty so that id is not directly count
    session.commit() # commit the updated id
    process = Process(
        id=q_process.id,
        equipment=[],
        final_outputs=[])

    return process, 200

@keycontrol.restricted(requires=AT_LEAST_AUDITOR)
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
    qProcess = application_map.Process
    qTower = application_map.Tower
    qEquipment = application_map.Equipment
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    try:
        q_process = q_tower.processes.filter(qProcess.id==process_id).one()
        equipment = [e.id for e in q_process.equipment]

        process_tree = ProcessTree.fromId(q_process.id)
        endpoints = process_tree.production_endpoints()

        final_outputs = [e.resource for e in q_process.equipment.filter(qEquipment.id.in_(endpoints))]
        # final_outputs = [e.id for e in endpoints]
        process = Process(
            id=q_process.id,
            equipment=equipment,
            final_outputs=final_outputs) # not fully implemnted yet

        return process, 200

    except NoResultFound:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

@keycontrol.restricted(requires=AT_LEAST_DIRECTOR)
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
    qProcess = application_map.Process
    qTower = application_map.Tower
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    try:
        q_process = q_tower.processes.filter(qProcess.id==process_id).one()
        session.delete(q_process)
        session.commit()
        return None,200

    except NoResultFound:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

@keycontrol.restricted(requires=AT_LEAST_MANAGER)
def towers_tower_id_processes_process_id_link_post(tower_id, process_id, link, api_key):
    """
    towers_tower_id_processes_process_id_link_post
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param link: 
    :type link: dict | bytes
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: None
    """
    if connexion.request.is_json:
        link = Link.from_dict(connexion.request.get_json())

    qEquipment = application_map.Equipment
    qEquipmentInfo = info_map.Equipment
    qTower = application_map.Tower
    qProcess = application_map.Process
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    q_process = q_tower.processes.filter(qProcess.id==process_id).one_or_none()
    if q_process is None or q_process.id != process_id:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

    # testing to see if the equipment are even valid
    try:
        q_source = session.query(qEquipment).filter(and_(qEquipment.id==link.source, qEquipment.process_id==process_id)).one()
        q_target = session.query(qEquipment).filter(and_(qEquipment.id==link.target, qEquipment.process_id==process_id)).one()
        make_link(link.source,link.target,link.material)

    except NoResultFound:
        error = Error('Equipment to link not found.')
        return error, 400
    except InvalidLinkMaterial as e:
        return Error(message=str(e)), 400




@keycontrol.restricted(requires=AT_LEAST_AUDITOR)
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
    qEquipment = application_map.Equipment
    qEquipmentInfo = info_map.Equipment
    qTower = application_map.Tower
    qProcess = application_map.Process
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404
    # find process
    q_process = q_tower.processes.filter(qProcess.id==process_id).one_or_none()
    if q_process is None or q_process.id != process_id:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

    equipment = []
    for e in q_process.equipment:
        equipment.append(Equipment(
            id=e.id,
            type=e.type,
            name=e.name,
            resource=e.resource,
            contains=e.contains,
            last_updated=e.last_updated,
            online=e.online,
            inputs=[Link(source=l.source,material=l.resource) for l in e.inputs],
            outputs=[Link(target=l.target,material=l.resource) for l in e.outputs])) # need to implement links still

    return equipment, 200

@keycontrol.restricted(requires=AT_LEAST_MANAGER)
def towers_tower_id_processes_process_id_equipment_post(tower_id, process_id, equipment, api_key):
    """
    towers_tower_id_processes_process_id_equipment_post
    
    :param tower_id: Tower Id number to look under.
    :type tower_id: int
    :param process_id: Process Id number to look under.
    :type process_id: int
    :param equipment: 
    :type equipment: dict | bytes
    :param api_key: Operation Access Key
    :type api_key: str

    :rtype: Equipment
    """
    if connexion.request.is_json:
        equipment = Equipment.from_dict(connexion.request.get_json())

    try:   
        # check if equipment type is valid and set the default name
        info_session = info_map.Session()
        qEquipmentInfo = info_map.Equipment
        default_name = info_session.query(qEquipmentInfo).filter(qEquipmentInfo.type==equipment.type).one().name
    except NoResultFound:
        error = Error('Equipment of type `{}` not valid.'.format(equipment.type))
        return error, 400

    qEquipment = application_map.Equipment

    qTower = application_map.Tower
    qProcess = application_map.Process
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    q_process = q_tower.processes.filter(qProcess.id==process_id).one_or_none()
    if q_process is None or q_process.id != process_id:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

    # validate resource
    if equipment.resource is not None:
        try:
            if not resource_allowed(equipment.type,equipment.resource):
                error = Error('Resource `{}` not allowed in equipment of type `{}`.'.format(equipment.resource,equipment.type))
                return error, 400
        except EquipmentNotFound as e:
            error = Error(message=str(e))
            return error, 400
        except ResourceNotFound as e:
            error = Error(message=str(e))
            return error, 400

    # set defaults if values not included
    equipment.name = equipment.name or default_name
    equipment.contains = equipment.contains or 0
    equipment.online = equipment.online or False
    equipment.last_updated = int(time.time())
    equipment.inputs = []
    equipment.outputs = []

    q_equipment = qEquipment(
        last_updated=equipment.last_updated,
        resource=equipment.resource,
        contains=equipment.contains,
        type=equipment.type,
        name=equipment.name,
        online=equipment.online)

    q_process.equipment.append(q_equipment)
    session.commit()
    q_equipment.id += random.randint(0,49) # add some uncertainty so that id is not directly count
    equipment.id = q_equipment.id
    session.commit()

    

    return equipment, 200

@keycontrol.restricted(requires=AT_LEAST_MANAGER)
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
    qEquipment = application_map.Equipment
    qEquipmentInfo = info_map.Equipment
    qTower = application_map.Tower
    qProcess = application_map.Process
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    # find process
    q_process = q_tower.processes.filter(qProcess.id==process_id).one_or_none()
    if q_process is None or q_process.id != process_id:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

    q_equipment = q_process.equipment.filter(qEquipment.id==equipment_id).one_or_none()
    if q_equipment is None or q_equipment.id != equipment_id:
        error = Error('Equipment `{}` not Found'.format(equipment_id))
        return error, 404
    
    session.delete(q_equipment)
    session.commit()

    return None, 200



@keycontrol.restricted(requires=AT_LEAST_AUDITOR)
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
    qEquipment = application_map.Equipment
    qEquipmentInfo = info_map.Equipment
    qTower = application_map.Tower
    qProcess = application_map.Process
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404

    # find process
    q_process = q_tower.processes.filter(qProcess.id==process_id).one_or_none()
    if q_process is None or q_process.id != process_id:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

    q_equipment = q_process.equipment.filter(qEquipment.id==equipment_id).one_or_none()
    if q_equipment is None or q_equipment.id != equipment_id:
        error = Error('Equipment `{}` not Found'.format(equipment_id))
        return error, 404

    equipment = Equipment(
        id=q_equipment.id,
        type=q_equipment.type,
        name=q_equipment.name,
        resource=q_equipment.resource,
        contains=q_equipment.contains,
        last_updated=q_equipment.last_updated,
        online=q_equipment.online,
        inputs=[Link(source=l.source,material=l.resource) for l in q_equipment.inputs],
        outputs=[Link(target=l.target,material=l.resource) for l in q_equipment.outputs])

    return equipment, 200

@keycontrol.restricted(requires=AT_LEAST_MANAGER)
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

    qEquipment = application_map.Equipment
    qEquipmentInfo = info_map.Equipment
    qTower = application_map.Tower
    qProcess = application_map.Process
    session = application_map.Session()

    # find the tower
    q_tower = session.query(qTower).filter(qTower.id == tower_id).one_or_none()
    if q_tower is None or q_tower.op_id != api_key.operation_id:
        error = Error('Tower `{}` not Found'.format(tower_id))
        return error, 404
    # find process
    q_process = q_tower.processes.filter(qProcess.id==process_id).one_or_none()
    if q_process is None or q_process.id != process_id:
        error = Error('Process `{}` not Found'.format(process_id))
        return error, 404

    q_equipment = q_process.equipment.filter(qEquipment.id==equipment_id).one_or_none()
    if q_equipment is None or q_equipment.id != equipment_id:
        error = Error('Equipment `{}` not Found'.format(equipment_id))
        return error, 404

    q_equipment.name = equipment.name or q_equipment.name

    if equipment.resource != q_equipment.resource:
        if resource_allowed(q_equipment.type, equipment.resource):
            for q_link in q_equipment.links:
                session.delete(q_link)
            q_equipment.resource = equipment.resource
        else:
            return Error('Invalid resource for this equipment.'), 400


    q_equipment.contains = equipment.contains or q_equipment.resource
    q_equipment.last_updated = equipment.last_updated or q_equipment.last_updated
    q_equipment.online = equipment.online or q_equipment.online
    session.commit()
    equipment = Equipment(
        id=q_equipment.id,
        type=q_equipment.type,
        name=q_equipment.name,
        resource=q_equipment.resource,
        contains=q_equipment.contains,
        last_updated=q_equipment.last_updated,
        online=q_equipment.online,
        inputs=[Link(source=l.source,material=l.resource) for l in q_equipment.inputs],
        outputs=[Link(target=l.target,material=l.resource) for l in q_equipment.outputs]) 

    return equipment, 200

