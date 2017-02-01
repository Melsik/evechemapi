import connexion
from evechem_api.models.equipment_info import EquipmentInfo
from evechem_api.models.error import Error
from evechem_api.models.group import Group
from evechem_api.models.material_info import MaterialInfo
from evechem_api.models.reaction import Reaction
from evechem_api.models.tower_info import TowerInfo
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

from evechem_api.sqla_maps import info_map

def info_equipment_get():
    """
    info_equipment_get
    Gets **array** of all equipment information. 

    :rtype: List[EquipmentInfo]
    """
    return 'do some magic!'


def info_equipment_reactors_get():
    """
    info_equipment_reactors_get
    Gets **array** of all &#x60;reactor&#x60; type equipment. 

    :rtype: List[EquipmentInfo]
    """
    return 'do some magic!'


def info_equipment_silos_get():
    """
    info_equipment_silos_get
    Gets **array** of all &#x60;silo&#x60; type equipment. 

    :rtype: List[EquipmentInfo]
    """
    return 'do some magic!'


def info_equipment_type_id_get(type_id):
    """
    ...
    Gets information about a specific silo or reactor of type &#x60;type_id&#x60;.
    :param type_id: Type of the item that needs fetched.
    :type type_id: float

    :rtype: EquipmentInfo
    """
    return 'do some magic!'


def info_materials_booster_get():
    """
    info_materials_booster_get
    Gets **array** of information for materials belonging to the &#x60;pure_booster&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    return 'do some magic!'


def info_materials_composites_get():
    """
    info_materials_composites_get
    Gets **array** of information for materials belonging to the &#x60;composites&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    return 'do some magic!'


def info_materials_gas_get():
    """
    info_materials_gas_get
    Gets **array** of information for materials belonging to the &#x60;wh_gas&#x60; or &#x60;booster_gas&#x60; groups. 

    :rtype: List[MaterialInfo]
    """
    return 'do some magic!'


def info_materials_get():
    """
    info_materials_get
    Get **array** of information for all materials, or if an array of &#x60;type_ids&#x60; is included, information on only those materials. 

    :rtype: List[MaterialInfo]
    """
    return 'do some magic!'


def info_materials_groups_get():
    """
    info_materials_groups_get
    Get **array** of information for all materials, or if an array of &#x60;type_ids&#x60; is included, information on only those materials. 

    :rtype: List[Group]
    """
    return 'do some magic!'


def info_materials_intermediates_get():
    """
    info_materials_intermediates_get
    Gets **array** of information for materials belonging to the &#x60;intermediates&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    return 'do some magic!'


def info_materials_polymer_get():
    """
    info_materials_polymer_get
    Gets **array** of information for materials belonging to the &#x60;hybrid_polymer&#x60; group. 

    :rtype: List[MaterialInfo]
    """
    return 'do some magic!'


def info_materials_raw_get():
    """
    info_materials_raw_get
    Gets **array** of information for materials belonging to the &#x60;raw&#x60; (mined moon resource) group. 

    :rtype: List[MaterialInfo]
    """
    return 'do some magic!'


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
    return 'do some magic!'


def info_reactions_complex_get():
    """
    info_reactions_complex_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;complex_reaction&#x60; group. 

    :rtype: List[Reaction]
    """
    return 'do some magic!'


def info_reactions_get():
    """
    info_reactions_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to any &#x60;reaction&#x60; group. 

    :rtype: List[Reaction]
    """
    return 'do some magic!'


def info_reactions_polymer_get():
    """
    info_reactions_polymer_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;biochemical_simple_reactions&#x60; group. 

    :rtype: List[Reaction]
    """
    return 'do some magic!'


def info_reactions_simple_biochemical_get():
    """
    info_reactions_simple_biochemical_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;simple_biochemical_reaction&#x60; group. 

    :rtype: List[Reaction]
    """
    return 'do some magic!'


def info_reactions_simple_get():
    """
    info_reactions_simple_get
    Gets **array** of all information for &#x60;reaction&#x60; items that belong to the &#x60;simple_reaction&#x60; or &#x60;unrefined_simple_reaction&#x60; groups. 

    :rtype: List[Reaction]
    """
    return 'do some magic!'


def info_reactions_type_id_get(type_id):
    """
    info_reactions_type_id_get
    Gets information about a specific reaction of type &#x60;type_id&#x60;. 
    :param type_id: Type of the item that needs fetched.
    :type type_id: float

    :rtype: Reaction
    """
    return 'do some magic!'


def info_towers_get():
    """
    info_towers_get
    Gets **array** of all tower information. 

    :rtype: List[TowerInfo]
    """
    return 'do some magic!'


def info_towers_type_id_get(type_id):
    """
    info_towers_type_id_get
    Gets type details for a specific tower with &#x60;type_id&#x60;. 
    :param type_id: Type of the item that needs fetched.
    :type type_id: int

    :rtype: TowerInfo
    """
    return 'do some magic!'
