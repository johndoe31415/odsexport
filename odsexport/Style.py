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
from .Enums import HAlign, VAlign, LineType, ConditionType, NumberStyle

@dataclasses.dataclass(eq = True, frozen = True)
class Font():
	bold: bool = False
	italic: bool = False
	size_pt: int | None = None
	color: str | None = None
	name: str | None = None

@dataclasses.dataclass(eq = True, frozen = True)
class DataStyle():
	min_integer_digits: int | None = None
	decimal_places: int | None = None
	min_decimal_places: int | None = None
	number_style: NumberStyle = NumberStyle.Number
	suffix: str | None = None

	@classmethod
	def fixed_decimal_places(cls, count: int):
		return cls(min_integer_digits = 1, decimal_places = count, min_decimal_places = count)

	@classmethod
	def percent_fixed_decimal_places(cls, count: int):
		return cls(number_style = NumberStyle.Percent, suffix = " %", min_integer_digits = 1, decimal_places = count, min_decimal_places = count)

@dataclasses.dataclass(eq = True, frozen = True)
class LineStyle():
	line_type: LineType = LineType.Solid
	color: str = "#000000"
	width_pt: float = 0.75

	@property
	def style_str(self):
		return f"{self.width_pt:.4f}pt {self.line_type.value} {self.color}"

@dataclasses.dataclass(eq = True, frozen = True)
class BorderStyle():
	top: LineStyle | None = None
	bottom: LineStyle | None = None
	left: LineStyle | None = None
	right: LineStyle | None = None


@dataclasses.dataclass(eq = True, frozen = True)
class CellStyle():
	font: Font = dataclasses.field(default_factory = Font)
	halign: HAlign | None = None
	valign: VAlign | None = None
	rotation_angle: int | None = None
	wrap: bool = False
	data_style: DataStyle | None = None
	background_color: str | None = None
	border: BorderStyle | None = None

@dataclasses.dataclass(eq = True, frozen = True)
class FormatCondition():
	condition: str
	cell_style: CellStyle

@dataclasses.dataclass(eq = True, frozen = True)
class ConditionalFormat():
	target: "CellRange"
	conditions: tuple[FormatCondition]
	condition_type: ConditionType = ConditionType.CellValue
	base_cell: "Cell | None" = None

@dataclasses.dataclass(eq = True, frozen = True)
class RowStyle():
	hidden: bool = False
	height: str | None = None

@dataclasses.dataclass(eq = True, frozen = True)
class ColStyle():
	hidden: bool = False
	width: str | None = None

@dataclasses.dataclass(eq = True, frozen = True)
class DataTable():
	cell_range: "CellRange"
