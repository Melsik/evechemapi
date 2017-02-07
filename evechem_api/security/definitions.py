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

	def __init__(self, key_value, operation_id, permissions):
		super(APIKey, self).__init__(key_value, permissions)
		self.operation_id = operation_id

	@classmethod
	def lookup(cls, key_value):
		session = application_map.Session()
		q = session.query(application_map.Key).filter(application_map.Key.key == key_value)
		q_key = q.one_or_none()
		if q_key is not None:
			key= cls(
				key_value=q_key.key,
				operation_id=q_key.operation_id,
				permissions=[q_key.permission.name]
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
