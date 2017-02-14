from .base import BaseKey, BaseKeyControl
from .exceptions import KeyNotFound
from evechem_api.maps import application_map

from evechem_api.models import Error

class APIKey(BaseKey):
	valid_permissions = [
		'master',
		'director',
		'manager',
		'auditor',
		'customer']

	def __init__(self, value, operation_id, permissions, name):
		super(APIKey, self).__init__(value, permissions)
		self.operation_id = operation_id
		self.name = name

	@classmethod
	def lookup(cls, key_value):
		qKey = application_map.Key
		session = application_map.Session()
		q = session.query(qKey).filter(qKey.value == key_value)
		q_key = q.one_or_none()
		if q_key is not None:
			key= cls(
				value=q_key.value,
				operation_id=q_key.operation_id,
				permissions=[q_key.permission],
				name=q_key.name
				)
			return key
		else:
			raise KeyNotFound("Key {} was not found.".format(key_value))

class APIKeyControl(BaseKeyControl):

	def auth_required(self):
		error = Error('Authentication Required')
		return error, 401
	def unauthorized(self):
		error = Error('Key was invalid or insufficient')
		return error, 403
