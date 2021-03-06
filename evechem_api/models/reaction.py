# coding: utf-8

from __future__ import absolute_import
from evechem_api.models.reaction_material import ReactionMaterial
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class Reaction(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, type: int=None, name: str=None, outputs: List[ReactionMaterial]=None, inputs: List[ReactionMaterial]=None ):
        """
        Reaction - a model defined in Swagger

        :param inputs: The inputs of this Reaction.
        :type inputs: List[ReactionMaterial]
        :param name: The name of this Reaction.
        :type name: str
        :param outputs: The outputs of this Reaction.
        :type outputs: List[ReactionMaterial]
        :param type: The type of this Reaction.
        :type type: int
        """
        self.swagger_types = {
            'type': int,
            'name': str,
            'outputs': List[ReactionMaterial],
            'inputs': List[ReactionMaterial]          
            
            
        }

        self.attribute_map = {
            'type': 'type',
            'name': 'name',
            'outputs': 'outputs',
            'inputs': 'inputs'
        }

        self._inputs = inputs
        self._name = name
        self._outputs = outputs
        self._type = type

    @classmethod
    def from_dict(cls, dikt) -> 'Reaction':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The reaction of this Reaction.
        :rtype: Reaction
        """
        return deserialize_model(dikt, cls)

    @property
    def inputs(self) -> List[ReactionMaterial]:
        """
        Gets the inputs of this Reaction.
        input material types and amounts 

        :return: The inputs of this Reaction.
        :rtype: List[ReactionMaterial]
        """
        return self._inputs

    @inputs.setter
    def inputs(self, inputs: List[ReactionMaterial]):
        """
        Sets the inputs of this Reaction.
        input material types and amounts 

        :param inputs: The inputs of this Reaction.
        :type inputs: List[ReactionMaterial]
        """

        self._inputs = inputs

    @property
    def name(self) -> str:
        """
        Gets the name of this Reaction.
        name of reaction 

        :return: The name of this Reaction.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """
        Sets the name of this Reaction.
        name of reaction 

        :param name: The name of this Reaction.
        :type name: str
        """

        self._name = name

    @property
    def outputs(self) -> List[ReactionMaterial]:
        """
        Gets the outputs of this Reaction.
        output material types and amounts 

        :return: The outputs of this Reaction.
        :rtype: List[ReactionMaterial]
        """
        return self._outputs

    @outputs.setter
    def outputs(self, outputs: List[ReactionMaterial]):
        """
        Sets the outputs of this Reaction.
        output material types and amounts 

        :param outputs: The outputs of this Reaction.
        :type outputs: List[ReactionMaterial]
        """

        self._outputs = outputs

    @property
    def type(self) -> int:
        """
        Gets the type of this Reaction.
        eve type_id number of material 

        :return: The type of this Reaction.
        :rtype: int
        """
        return self._type

    @type.setter
    def type(self, type: int):
        """
        Sets the type of this Reaction.
        eve type_id number of material 

        :param type: The type of this Reaction.
        :type type: int
        """

        self._type = type

