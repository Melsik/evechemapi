import connexion
from evechem_api.models.equipment_info import EquipmentInfo
from evechem_api.models.equipment_info_fitting import EquipmentInfoFitting
from evechem_api.models.error import Error
from evechem_api.models.group import Group
from evechem_api.models.material_info import MaterialInfo
from evechem_api.models.reaction import Reaction
from evechem_api.models.reaction_material import ReactionMaterial
from evechem_api.models.tower_info import TowerInfo
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

from evechem_api.maps import info_map
from sqlalchemy.orm import aliased

def _material_by_group(*group_ids):
    """
    _material_by_group
    NOTE: Helper Function for other controllers, not independent.

    Gets list of `MaterialInfo` objects from the material table by matching group_ids.
    Search multiple groups by including them as extra parameters:

    >>> _material_by_group(428, 18)

    If no group is supplied, all materials are returned.

    :param group_ids: Group Ids of the item that needs fetched.
    :type group_ids: integer

    :rtype: List[MaterialInfo]
    """

    session = info_map.Session()
    if len(group_ids) > 0:
        q = session.query(info_map.Material).filter(info_map.Material.group_id.in_(group_ids))
    else:
        q = session.query(info_map.Material)

    mats = q.all() # return all rows from result
    if len(mats) == 0:
        return None

    materials = []
    for mat in mats:
        materials.append( MaterialInfo(
            type=mat.type,
            group=mat.group_id,
            name=mat.name,
            volume=mat.volume))

    return materials

def _equipment_by_group(*group_ids):
    """
    _reaction_by_group
    NOTE: Helper Function for other controllers, not independent.

    Gets list of `Equipment` objects from the reaction and reaction_io tables by matching group_ids.
    Search multiple groups by including them as extra parameters:

    >>> _equipment_by_group(662,484)

    If no group is supplied, all equipment are returned.

    :param group_ids: Group Ids of the item that needs fetched.
    :type group_ids: integer

    :rtype: List[Equipment]

    """
    session = info_map.Session()
    equipment_list = []
    if len(group_ids) == 0:
        q = session.query(info_map.Equipment)
    else:
        q = session.query(info_map.Equipment).filter(info_map.Equipment.group_id.in_(group_ids))

    q_equipment_list = q.all()

    if len(q_equipment_list) == 0:
        return None

    for q_equipment in q_equipment_list:
        equipment = EquipmentInfo(
            type=q_equipment.type,
            name=q_equipment.name,
            group=q_equipment.group_id,
            capacity=q_equipment.capacity,
            fitting=EquipmentInfoFitting(
                cpu=q_equipment.cpu,
                powergrid=q_equipment.powergrid),
            allowed_groups=[g.group_id for g in q_equipment.groups])

        equipment_list.append(equipment)

    return equipment_list

def _reaction_by_group(*group_ids):
    """
    _reaction_by_group
    NOTE: Helper Function for other controllers, not independent.

    Gets list of `Reaction` objects from the reaction and reaction_io tables by matching group_ids.
    Search multiple groups by including them as extra parameters:

    >>> _reaction_by_group(662,484)

    If no group is supplied, all reactions are returned.

    :param group_ids: Group Ids of the item that needs fetched.
    :type group_ids: integer

    :rtype: List[Reaction]
    """
    session = info_map.Session()
    reactions = []
    if len(group_ids) == 0:
        q = session.query(info_map.Reaction)
    else:
        q = session.query(info_map.Reaction).filter(info_map.Reaction.group_id.in_(group_ids))
    q_reactions = q.all()
    if len(q_reactions) == 0:
        return None

    for q_reaction in q_reactions:

        outputs = []
        inputs = []
        for row in q_reaction.materials:
            reaction_mat = ReactionMaterial(
                type=row.material_id,
                name=row.material.name,
                amount=row.quantity
                )

            if row.is_input:
                inputs.append(reaction_mat)
            else:
                outputs.append(reaction_mat)

        reaction = Reaction(
            type=q_reaction.type,
            name=q_reaction.name,
            inputs=inputs,
            outputs=outputs) 

        reactions.append(reaction)

    return reactions

def _reaction_by_type(type_id):
    """
    _reaction_by_type
    NOTE: Helper Function for other controllers, not independent.

    Gets a `Reaction` object from the material table by matching type_id.

    :param group_ids: Group Ids of the item that needs fetched.
    :type group_ids: integer

    :rtype: List[Reaction]
    """
    session = info_map.Session()

    q = session.query(info_map.Reaction).filter(info_map.Reaction.type==type_id)
    q_reaction = q.one_or_none()
    if q_reaction is None:
        return None

    outputs = []
    inputs = []
    for row in q_reaction.materials:
        reaction_mat = ReactionMaterial(
            type=row.material_id,
            name=row.material.name,
            amount=row.quantity
            )

        if row.is_input:
            inputs.append(reaction_mat)
        else:
            outputs.append(reaction_mat)

    reaction = Reaction(
        type=q_reaction.type,
        name=q_reaction.name,
        inputs=inputs,
        outputs=outputs) 

    return reaction


def info_equipment_get():
    """
    info_equipment_get
    Gets **array** of all equipment information. 

    :rtype: List[EquipmentInfo]
    """
    equipment = _equipment_by_group()
    return equipment, 200


def info_equipment_reactors_get():
    """
    info_equipment_reactors_get
    Gets **array** of all &#x60;reactor&#x60; type equipment. 

    :rtype: List[EquipmentInfo]
    """
    equipment = _equipment_by_group(438) # 438 == Mobile Reactor
    return equipment, 200


def info_equipment_silos_get():
    """
    info_equipment_silos_get
    Gets **array** of all &#x60;silo&#x60; type equipment. 

    :rtype: List[EquipmentInfo]
    """
    equipment = _equipment_by_group(404) # 404 == Silo
    return equipment, 200


def info_equipment_type_id_get(type_id):
    """
    ...
    Gets information about a specific silo or reactor of type &#x60;type_id&#x60;.
    :param type_id: Type of the item that needs fetched.
    :type type_id: float

    :rtype: EquipmentInfo
    """
    session = info_map.Session()

    q = session.query(info_map.Equipment).filter(info_map.Equipment.type == type_id)
    q_equipment = q.one_or_none()

    if q_equipment is not None:
        equipment = EquipmentInfo(
            type=q_equipment.type,
            name=q_equipment.name,
            group=q_equipment.group_id,
            capacity=q_equipment.capacity,
            fitting=EquipmentInfoFitting(
                cpu=q_equipment.cpu,
                powergrid=q_equipment.powergrid),
            allowed_groups=[g.group_id for g in q_equipment.groups])

        return equipment

    else:
        error = Error('Type {} Not Found'.format(type_id))
        return error, 404


def info_materials_booster_get():
    """
    info_materials_booster_get
    Gets **array** of information for materials belonging to the &#x60;pure_booster&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    materials = _material_by_group(712) # 712 == intermediate group
    return materials, 200


def info_materials_composites_get():
    """
    info_materials_composites_get
    Gets **array** of information for materials belonging to the &#x60;composites&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    materials = _material_by_group(429) # 429 == intermediate group
    return materials, 200


def info_materials_gas_get():
    """
    info_materials_gas_get
    Gets **array** of information for materials belonging to the &#x60;wh_gas&#x60; or &#x60;booster_gas&#x60; groups. 

    :rtype: List[MaterialInfo]
    """
    materials = _material_by_group(711) # 711 == intermediate group
    return materials, 200


def info_materials_get():
    """
    info_materials_get
    Get **array** of information for all materials, or if an array of &#x60;type_ids&#x60; is included, information on only those materials. 

    :rtype: List[MaterialInfo]
    """
    materials = _material_by_group() # empty means all groups
    return materials, 200


def info_materials_groups_get():
    """
    info_materials_groups_get
    Get **array** of information for all materials, or if an array of &#x60;type_ids&#x60; is included, information on only those materials. 

    :rtype: List[Group]
    """
    session = info_map.Session()

    mat = aliased(info_map.Material)
    grp = aliased(info_map.Group)

    q = session.query(mat.group_id,grp.name).join(grp).distinct()
    groups = [Group(group=row.group_id,name=row.name) for row in q.all()]
    return groups, 200


def info_materials_intermediates_get():
    """
    info_materials_intermediates_get
    Gets **array** of information for materials belonging to the &#x60;intermediates&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    materials = _material_by_group(428) # 428 == intermediate group
    return materials, 200


def info_materials_polymer_get():
    """
    info_materials_polymer_get
    Gets **array** of information for materials belonging to the &#x60;hybrid_polymer&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    materials = _material_by_group(974) # 974 == intermediate group
    return materials, 200


def info_materials_raw_get():
    """
    info_materials_raw_get
    Gets **array** of information for materials belonging to the &#x60;raw&#x60; (mined moon resource) group. 

    :rtype: List[MaterialInfo]
    """
    materials = _material_by_group(427) # 427 == intermediate group
    return materials, 200


def info_materials_type_id_get(type_id):
    """
    info_materials_type_id_get
    Gets type details for a specific item with &#x60;type_id&#x60;. 
    :param type_id: Type of the item that needs fetched.
    :type type_id: int

    :rtype: MaterialInfo
    """
    session = info_map.Session()
    q = session.query(info_map.Material).filter(info_map.Material.type == type_id)

    mat = q.one_or_none() # return the only result or `None`

    if mat is not None:
        material_info = MaterialInfo(
            type=mat.type,
            group=mat.group_id,
            name=mat.name,
            volume=mat.volume)
        return material_info, 200
    else:
        error = Error('Type {} Not Found'.format(type_id))
        return error, 404

def info_reactions_complex_biochemical_get():
    """
    info_reactions_complex_biochemical_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;complex_biochemical_reaction&#x60;group. 

    :rtype: List[Reaction]
    """
    reactions = _reaction_by_group(662) # 662 == Complex Biochemical Reactions
    return reactions, 200


def info_reactions_complex_get():
    """
    info_reactions_complex_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;complex_reaction&#x60; group. 

    :rtype: List[Reaction]
    """
    reactions = _reaction_by_group(484) # 484 == Complex Reactions
    return reactions, 200


def info_reactions_get():
    """
    info_reactions_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to any &#x60;reaction&#x60; group. 

    :rtype: List[Reaction]
    """
    reactions = _reaction_by_group()
    return reactions, 200



def info_reactions_polymer_get():
    """
    info_reactions_polymer_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;biochemical_simple_reactions&#x60; group. 

    :rtype: List[Reaction]
    """
    reactions = _reaction_by_group(977) # 977 == Hybrid Reactions
    return reactions, 200


def info_reactions_simple_biochemical_get():
    """
    info_reactions_simple_biochemical_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;simple_biochemical_reaction&#x60; group. 

    :rtype: List[Reaction]
    """
    reactions = _reaction_by_group(661) # 661 == Simple Biochemical Reactions
    return reactions, 200


def info_reactions_simple_get():
    """
    info_reactions_simple_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;simple_reaction&#x60; or &#x60;unrefined_simple_reaction&#x60; groups. 

    :rtype: List[Reaction]
    """
    reactions = _reaction_by_group(436) # 436 == Simple Reaction
    return reactions, 200


def info_reactions_type_id_get(type_id):
    """
    info_reactions_type_id_get
    Gets information about a specific reaction of type &#x60;type_id&#x60;. 
    :param type_id: Type of the item that needs fetched.
    :type type_id: float

    :rtype: Reaction
    """
    reactions = _reaction_by_type(type_id)
    if reactions is None:
        error = Error('Type {} Not Found'.format(type_id))
        return error, 404
    else:
        return reactions, 200


def info_towers_get():
    """
    info_towers_get
    Gets **array** of all tower information. 

    :rtype: List[TowerInfo]
    """
    session = info_map.Session()

    q = session.query(info_map.Tower)
    q_towers = q.all()
    towers = []
    for q_tower in q_towers:
        tower = TowerInfo(
            type=q_tower.type,
            fuel_bay=q_tower.fuel_bay,
            stront_bay=q_tower.stront_bay,
            name=q_tower.name,
            storage_mult=q_tower.storage_mult,
            cpu=q_tower.cpu,
            powergrid=q_tower.powergrid,
            fuel_usage=q_tower.fuel_usage,
            stront_usage=q_tower.stront_usage,
            fuel_type=q_tower.fuel_type)

        towers.append(tower)

    return towers, 200


def info_towers_type_id_get(type_id):
    """
    info_towers_type_id_get
    Gets type details for a specific tower with &#x60;type_id&#x60;. 
    :param type_id: Type of the item that needs fetched.
    :type type_id: int

    :rtype: TowerInfo
    """
    session = info_map.Session()

    q = session.query(info_map.Tower).filter(info_map.Tower.type==type_id)
    q_tower = q.one_or_none()

    if q_tower is None:
        error = Error('Type {} Not Found'.format(type_id))
        return error, 404
    else:
        tower = TowerInfo(
            type=q_tower.type,
            fuel_bay=q_tower.fuel_bay,
            stront_bay=q_tower.stront_bay,
            name=q_tower.name,
            storage_mult=q_tower.storage_mult,
            cpu=q_tower.cpu,
            powergrid=q_tower.powergrid,
            fuel_usage=q_tower.fuel_usage,
            stront_usage=q_tower.stront_usage,
            fuel_type=q_tower.fuel_type)

        return tower, 200


