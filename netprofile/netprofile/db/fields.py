from sqlalchemy import (
	and_,
	schema,
	types,
	util
)

from sqlalchemy.dialects import (
	mssql,
	mysql,
	oracle,
	postgresql
)

from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

from netprofile.db import processors
from netprofile.common import ipaddr

import re

_D_MYSQL = frozenset([
	mysql.mysqlconnector.dialect,
	mysql.mysqldb.dialect,
	mysql.oursql.dialect,
	mysql.pymysql.dialect,
	mysql.pyodbc.dialect,
	mysql.zxjdbc.dialect
])

_D_PGSQL = frozenset([
	postgresql.pg8000.dialect,
	postgresql.psycopg2.dialect,
	postgresql.pypostgresql.dialect,
	postgresql.zxjdbc.dialect
])

_D_ORA = frozenset([
	oracle.cx_oracle.dialect,
	oracle.zxjdbc.dialect
])

_D_MSSQL = frozenset([
	mssql.adodbapi.dialect,
	mssql.mxodbc.dialect,
	mssql.pymssql.dialect,
	mssql.pyodbc.dialect,
	mssql.zxjdbc.dialect
])

def _is_mysql(d):
	return d.__class__ in _D_MYSQL

def _is_pgsql(d):
	return d.__class__ in _D_PGSQL

def _is_ora(d):
	return d.__class__ in _D_ORA

def _is_mssql(d):
	return d.__class__ in _D_MSSQL

class IPv4Address(types.TypeDecorator):
	"""
	Hybrid IPv4 address.
	"""
	impl = types.Integer

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.INTEGER(unsigned=True)
		if _is_pgsql(dialect):
			return postgresql.INET()
		return self.impl

	@property
	def python_type(self):
		return ipaddr.IPv4Address

	def process_bind_param(self, value, dialect):
		if value is None:
			return None
		if _is_pgsql(dialect):
			return str(value)
		return int(value)

	def process_result_value(self, value, dialect):
		if value is None:
			return None
		return ipaddr.IPv4Address(value)

class IPv6Address(types.TypeDecorator):
	"""
	Hybrid IPv6 address.
	"""
	impl = types.Numeric(precision=39, scale=0)

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.DECIMAL(precision=39, scale=0, unsigned=True)
		if _is_pgsql(dialect):
			return postgresql.INET()
		return self.impl

	@property
	def python_type(self):
		return ipaddr.IPv6Address

	def process_bind_param(self, value, dialect):
		if value is None:
			return None
		if _is_pgsql(dialect):
			return str(value)
		return int(value)

	def process_result_value(self, value, dialect):
		if value is None:
			return None
		return ipaddr.IPv6Address(value)

class NPBoolean(types.TypeDecorator, types.SchemaType):
	"""
	An almost-normal boolean type with a special case for MySQL.
	"""
	impl = types.Boolean

	def __init__(self, **kw):
		types.TypeDecorator.__init__(self, **kw)
		types.SchemaType.__init__(self, **kw)

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.ENUM('Y', 'N', charset='ascii', collation='ascii_bin')
		return types.Boolean(name='ck_boolean')

	def _should_create_constraint(self, compiler):
		return (not compiler.dialect.supports_native_boolean) \
				and (not _is_mysql(compiler.dialect))

	def _set_table(self, column, table):
		e = schema.CheckConstraint(
			column.in_([0, 1]),
			name=self.name,
			_create_rule=util.portable_instancemethod(
				self._should_create_constraint)
			)
		table.append_constraint(e)

	@property
	def python_type(self):
		return bool

#	def process_bind_param(self, value, dialect):
#		if value is None:
#			return None
#		if isinstance(dialect, mysql.dialect):
#			if value:
#				return 'Y'
#			return 'N'
#		return value
#
#	def process_result_value(self, value, dialect):
#		if value is None:
#			return None
#		if isinstance(dialect, mysql.dialect):
#			if value == 'Y':
#				return True
#			return False
#		return value

	def bind_processor(self, dialect):
		if _is_mysql(dialect):
			return processors.boolean_to_enum
		else:
			return None

	def result_processor(self, dialect, coltype):
		if _is_mysql(dialect):
			return processors.enum_to_boolean
		else:
			return None

class npbool(expression.FunctionElement):
	"""
	Constant NPBoolean element.
	"""
	type = NPBoolean()

	def __init__(self, val):
		self.val = val

@compiles(npbool, 'mysql')
def my_npbool(element, compiler, **kw):
	if element.val:
		return '\'Y\''
	return '\'N\''

@compiles(npbool, 'sqlite')
def sq_npbool(element, compiler, **kw):
	if element.val:
		return '1'
	return '0'

@compiles(npbool)
def compile_npbool(element, compiler, **kw):
	if element.val:
		return 'TRUE'
	return 'FALSE'

class ASCIIString(types.TypeDecorator):
	"""
	ASCII-only version of normal string field.
	"""
	impl = types.String

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.VARCHAR(self.impl.length, charset='ascii', collation='ascii_bin')
		return self.impl

class ASCIIFixedString(types.TypeDecorator):
	"""
	ASCII-only version of fixed-length string field.
	"""
	impl = types.CHAR

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.CHAR(self.impl.length, charset='ascii', collation='ascii_bin')
		return self.impl

class ExactUnicode(types.TypeDecorator):
	"""
	Case-honoring unicode string.
	"""
	impl = types.Unicode

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.VARCHAR(self.impl.length, charset='utf8', collation='utf8_bin')
		return self.impl

class Int8(types.TypeDecorator):
	"""
	8-bit signed integer field.
	"""
	impl = types.SmallInteger
	MIN_VALUE = -128
	MAX_VALUE = 127

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.TINYINT()
		return self.impl

class Int16(types.TypeDecorator):
	"""
	16-bit signed integer field.
	"""
	impl = types.SmallInteger
	MIN_VALUE = -32768
	MAX_VALUE = 32767

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.SMALLINT()
		return self.impl

class Int32(types.TypeDecorator):
	"""
	32-bit signed integer field.
	"""
	impl = types.Integer
	MIN_VALUE = -2147483648
	MAX_VALUE = 2147483647

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.INTEGER()
		return self.impl

class Int64(types.TypeDecorator):
	"""
	64-bit signed integer field.
	"""
	impl = types.BigInteger
	MIN_VALUE = -9223372036854775808
	MAX_VALUE = 9223372036854775807

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.BIGINT()
		return self.impl

class UInt8(types.TypeDecorator):
	"""
	8-bit unsigned integer field.
	"""
	impl = types.SmallInteger
	MIN_VALUE = 0
	MAX_VALUE = 255

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.TINYINT(unsigned=True)
		return self.impl

class UInt16(types.TypeDecorator):
	"""
	16-bit unsigned integer field.
	"""
	impl = types.SmallInteger
	MIN_VALUE = 0
	MAX_VALUE = 65535

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.SMALLINT(unsigned=True)
		return self.impl

class UInt32(types.TypeDecorator):
	"""
	32-bit unsigned integer field.
	"""
	impl = types.Integer
	MIN_VALUE = 0
	MAX_VALUE = 4294967295

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.INTEGER(unsigned=True)
		return self.impl

class UInt64(types.TypeDecorator):
	"""
	64-bit unsigned integer field.
	"""
	impl = types.Integer
	MIN_VALUE = 0
	MAX_VALUE = 18446744073709551615

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.BIGINT(unsigned=True)
		return self.impl

class EnumSymbol(expression.ClauseElement):
	"""
	Define a fixed symbol tied to a parent class.
	"""
	def __init__(self, cls_, name, value, description, order=0):
		self.cls_ = cls_
		self.name = name
		self.value = value
		self.description = description
		self.order = order

	def __reduce__(self):
		"""
		Allow unpickling to return the symbol linked to the DeclEnum class.
		"""
		return getattr, (self.cls_, self.name)

	def __iter__(self):
		return iter([self.value, self.description])

	def __repr__(self):
		return '<%s>' % self.name

	def json_repr(self):
		return self.value

@compiles(EnumSymbol)
def compile_enumsym(element, compiler, **kw):
	return compiler.sql_compiler.render_literal_value(element.value, None)

# FIXME: fix symbol order
class EnumMeta(type):
	"""
	Generate new DeclEnum classes.
	"""
	def __init__(cls, classname, bases, dict_):
		cls._reg = reg = cls._reg.copy()

		for k, v in dict_.items():
			if isinstance(v, tuple):
				sym = reg[v[0]] = EnumSymbol(cls, k, *v)
				setattr(cls, k, sym)
		return type.__init__(cls, classname, bases, dict_)

	def __iter__(cls):
		return iter(cls._reg.values())

class DeclEnumType(types.SchemaType, types.TypeDecorator):
	def __init__(self, enum):
		self.enum = enum
		self.name = 'ck%s' % re.sub(
			'([A-Z])',
			lambda m: '_' + m.group(1).lower(),
			enum.__name__
		)
		self.impl = types.Enum(*enum.values(), name=self.name)

	def load_dialect_impl(self, dialect):
		if _is_mysql(dialect):
			return mysql.ENUM(*self.enum.values(), charset='ascii', collation='ascii_bin')
		return self.impl

	def _set_table(self, column, table):
		self.impl._set_table(column, table)

	@property
	def python_type(self):
		return EnumSymbol

	def copy(self):
		return DeclEnumType(self.enum)

	def process_bind_param(self, value, dialect):
		if value is None:
			return None
		return value.value

	def process_result_value(self, value, dialect):
		if value is None:
			return None
		return self.enum.from_string(value.strip())

	def coerce_compared_value(self, op, value):
		if isinstance(value, str):
			return ASCIIString()
		return self

class DeclEnum(object, metaclass=EnumMeta):
	"""
	Declarative enumeration.
	"""
	_reg = {}

	@classmethod
	def from_string(cls, value):
		try:
			return cls._reg[value]
		except KeyError:
			raise ValueError(
				'Invalid value for %r: %r' %
				(cls.__name__, value)
			)

	@classmethod
	def values(cls):
		return sorted(cls._reg, key=lambda k: cls._reg[k].order)

	@classmethod
	def db_type(cls):
		return DeclEnumType(cls)

