from django.db import models
import json
from dataclasses import dataclass 
from typing import List

class KwargsKey:
	MaxLength = "max_length"
	Null = "null"
	Blank = "blank"
	AutoNow = "auto_now"
	AutoNowAdd = "auto_now_add"
	Unique = "unique"

@dataclass
class FieldKwargs:
	key_name: str
	validators: None 

def validate_bool(value):
	return isinstance(value, bool)

def validate_int(value):
	return isinstance(value, int)

max_length = FieldKwargs(KwargsKey.MaxLength, [validate_int])
null = FieldKwargs(KwargsKey.Null, [validate_bool])
blank = FieldKwargs(KwargsKey.Blank, [validate_bool])
unique = FieldKwargs(KwargsKey.Unique, [validate_bool])
auto_now = FieldKwargs(KwargsKey.AutoNow, [validate_bool])
auto_now_add = FieldKwargs(KwargsKey.AutoNowAdd, [validate_bool])

@dataclass
class Field:
	str_repr :str
	kwargs: List[FieldKwargs] = (null, blank)

class GenerateModel:
	'''
	Genarating django model codes, developer can copy and paste 
	the genarated codes into the models.py file.
	'''
	fields = []
	__fld_class_dict = {
		models.CharField: Field("models.CharField", (max_length, null, blank, unique)),
		models.TextField: Field("models.TextField", (max_length, null, blank, unique)),
		models.SlugField: Field('models.SlugField', (max_length, null, blank, unique)),
		models.DateTimeField: Field("models.DateTimeField", (auto_now_add, auto_now, null, blank, unique)),
	}

	def __init__(self, model_name):
		self.model_name = model_name

	def _get_fld_as_str(self, fld_class, kwargs):
		ret = self.__fld_class_dict.get(fld_class, None)
		if ret is None:
			raise ValueError("field class not exist in the field classes dictionary")
		keys = {fld_kwargs.key_name:fld_kwargs for fld_kwargs in ret.kwargs}
		res = []
		for k,v in kwargs.items():
			if not (k in keys):
				raise ValueError("key, value not correct to this field!!!")
			# print("validators--->", keys.get(k).validators)
			# print("value---->", v)
			res.extend([validator(v) for validator in keys.get(k).validators])

		print("res--->", res)
		if not all(res):
			raise ValueError("value errors in fields")

		return ret 

	def add_field(self, fld_name, fld_class, kwargs={}):
		kwargs_str = ",".join(["=".join([k,f'{v}' if not isinstance(v, str) \
						else f'"{v}"']) for k,v in  kwargs.items()])
		self.fields.append(
			f"{fld_name} = {self._get_fld_as_str(fld_class, kwargs).str_repr}({kwargs_str})"
		) 

	def clear(self):
		self.fields = []

	def add_fields(self, fld_names, flds_class, kwargs_list):
		if not (len(fld_names) == len(flds_class) == len(kwargs_list)):
			raise ValueError("arguments length are not same.")

		for i, j, k in zip(fld_names, flds_class, kwargs_list):
			self.add_field(i, j, k)

	def get_model_codes(self):
		print(f'''class {self.model_name}(models.Model):\n\t'''+"\n\t".join(self.fields))




# In [8]: gm.add_field("description", models.TextField, {"null": True, "max_length": 1000})
# res---> [True, True]

# In [9]: gm.add_field("title", models.CharField, {"max_length":255, "unique": True})
# res---> [True, True]

# In [10]: gm.add_field("posted_on", models.DateTimeField, {"auto_now": True})
# res---> [True]

# In [11]: gm.add_field("slug", models.SlugField, {"null": True})
# res---> [True]
