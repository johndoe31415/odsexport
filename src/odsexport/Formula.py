#	odsexport - Python-native ODS writer library
#	Copyright (C) 2024-2026 Johannes Bauer
#
#	This file is part of odsexport.
#
#	odsexport is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	odsexport is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with odsexport; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

from .Cell import Cell
from .CellRange import CellRange

class Expression():
	_BinaryOperation = None
	_Constant = None
	_Function = None
	_CellRef = None

	def __add__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "+", rhs = other)

	def __sub__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "-", rhs = other)

	def __mul__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "*", rhs = other)

	def __truediv__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "/", rhs = other)

	def __mod__(self, other: Expression):
		return self._Function("MOD", self, other)

	def __pow__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "^", rhs = other)

	def __lt__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "<", rhs = other)

	def __le__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "<=", rhs = other)

	def __gt__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = ">", rhs = other)

	def __ge__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = ">=", rhs = other)

	def __eq__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "=", rhs = other)

	def __ne__(self, other: Expression):
		return self._BinaryOperation(lhs = self, op = "<>", rhs = other)

	def __and__(self, other: Expression):
		return self._Function("AND", self, other)

	def __and__(self, other: Expression):
		return self._Function("AND", self, other)

	def __or__(self, other: Expression):
		return self._Function("OR", self, other)

	def _symmetric_round_positive_value(self, ndigits: int):
		multiplier = 10 ** ndigits
		testvalue = self * multiplier
		condition = testvalue.is_even() & ((testvalue % 1) <= 0.5)
		return condition.then(
						then_value = self._Function("ROUNDDOWN", self, ndigits),
						else_value = self.round(ndigits))

	def __round__(self, ndigits: int | None = None):
		if ndigits is None:
			ndigits = 0
		return self.sign() * (self.abs()._symmetric_round_positive_value(ndigits))

	def subttotal(self, function_name: str, include_hidden_cells: bool = True):
		return self._Function.subtotal(function_name, self, include_hidden_cells = include_hidden_cells)

	def min(self):
		return self._Function("MIN", self)

	def max(self):
		return self._Function("MAX", self)

	def sum(self):
		return self._Function("SUM", self)

	def count(self):
		return self._Function("COUNT", self)

	def average(self):
		return self._Function("AVERAGE", self)

	def average_unless_no_data(self, no_data_replacement: Expression | str = ""):
		condition = self.count() > 0
		return condition.then(self.average(), else_value = no_data_replacement)

	def abs(self):
		return self._Function("ABS", self)

	def sign(self):
		return self._Function("SIGN", self)

	def is_even(self):
		return self._Function("ISEVEN", self)

	def is_odd(self):
		return self._Function("ISODD", self)

	def round(self, ndigits: int | None = None):
		if ndigits is None:
			return self._Function("ROUND", self)
		else:
			return self._Function("ROUND", self, ndigits)

	def clamp(self, min_value: Expression, max_value: Expression):
		return self._Function("MEDIAN", min_value, self, max_value)

	def then(self, then_value: Expression, else_value: Expression | None = None):
		if else_value is None:
			return self._Function("IF", self, then_value)
		else:
			return self._Function("IF", self, then_value, else_value)

	@classmethod
	def wrap(cls, value: Expression | int | float | bool | str | Cell | CellRange):
		if isinstance(value, Expression):
			return value
		elif isinstance(value, (int, float, bool, str)):
			return cls._Constant(value)
		elif isinstance(value, (Cell, CellRange)):
			return cls._CellRef(value)
		else:
			raise NotImplementedError(type(value))

	def render(self, sheet: Sheet):
		raise NotImplementedError()


class Constant(Expression):
	def __init__(self, value: int | float | bool | str):
		self._value = value

	def render(self, sheet: Sheet):
		if isinstance(self._value, bool):
			return {
				False:	"FALSE()",
				True:	"TRUE()",
			}[self._value]
		elif isinstance(self._value, str):
			escaped = self._value.replace("\"", "\"\"")
			return f"\"{escaped}\""
		else:
			return str(self._value)
Expression._Constant = Constant


class BinaryOperation(Expression):
	def __init__(self, lhs: Expression, op: str, rhs: Expression):
		self._lhs = Expression.wrap(lhs)
		self._op = op
		self._rhs = Expression.wrap(rhs)

	def render(self, sheet: Sheet):
		return f"({self._lhs.render(sheet)}{self._op}{self._rhs.render(sheet)})"
Expression._BinaryOperation = BinaryOperation


class CellRef(Expression):
	def __init__(self, cell: Cell | CellRange):
		assert(isinstance(cell, (Cell, CellRange)))
		self._cell = cell

	def render(self, sheet: Sheet):
		if self._cell.sheet == sheet:
			return format(self._cell, "b")
		else:
			return format(self._cell, "ba")
Expression._CellRef = CellRef


class Function(Expression):
	__SUBTOTAL_IDS = { name: fnc_id for (fnc_id, name) in enumerate([ "AVERAGE", "COUNT", "COUNTA", "MAX", "MIN", "PRODUCT", "STDEV", "STDEVP", "SUM", "VAR", "VARP" ], 1) }

	def __init__(self, name: str, *args: list[Expression]):
		self._name = name
		self._args = [ Expression.wrap(arg) for arg in args ]

	def render(self, sheet: Sheet):
		return f"{self._name}({';'.join(arg.render(sheet) for arg in self._args)})"

	@classmethod
	def subtotal(cls, function_name: str, argument: Expression, include_hidden_cells: bool = True):
		function_id = cls.__SUBTOTAL_IDS[function_name]
		if not include_hidden_cells:
			function_id += 100
		return cls("SUBTOTAL", function_id, argument)
Expression._Function = Function
