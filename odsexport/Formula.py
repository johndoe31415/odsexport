#	odsexport - Python-native ODS writer library
#	Copyright (C) 2024-2024 Johannes Bauer
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

import dataclasses
from .Enums import CellValueType

@dataclasses.dataclass
class Formula():
	value: str
	value_type: CellValueType = CellValueType.Float

	@classmethod
	def clamp(cls, value: str, low_end: str, high_end: str):
		return f"MEDIAN({low_end};{value};{high_end})"

	@classmethod
	def if_then_else(cls, if_condition: str, then_value: str, else_value: str):
		return f"IF({if_condition};{then_value};{else_value})"

	@classmethod
	def _round_positive_value_half_to_even(cls, value: str, digits: int = 0):
		return cls.if_then_else(
				if_condition = f"AND(ISEVEN(({value})*10^{digits});MOD(({value})*10^{digits};1)<=0.5)",
				then_value = f"ROUNDDOWN({value};{digits})",
				else_value = f"ROUND({value};{digits})",
		)

	@classmethod
	def round_half_to_even(cls, value: str, digits: int = 0):
		return f"(SIGN({value})*{cls._round_positive_value_half_to_even(f'ABS({value})', digits = digits)})"
