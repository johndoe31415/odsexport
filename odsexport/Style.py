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
from .Enums import HAlign, VAlign, LineType, ConditionType

@dataclasses.dataclass(eq = True, frozen = True)
class Font():
	bold: bool = False
	italic: bool = False
	size_pt: int | None = None
	color: str | None = None
	name: str | None = None

class DataStyle(): pass

@dataclasses.dataclass(eq = True, frozen = True)
class DataStyleNumber(DataStyle):
	min_integer_digits: int | None = None
	decimal_places: int | None = None
	min_decimal_places: int | None = None
	prefix: str | None = None
	suffix: str | None = None

	@classmethod
	def fixed(cls, count: int):
		return cls(min_integer_digits = 1, decimal_places = count, min_decimal_places = count)

@dataclasses.dataclass(eq = True, frozen = True)
class DataStylePercent(DataStyle):
	min_integer_digits: int | None = None
	decimal_places: int | None = None
	min_decimal_places: int | None = None
	prefix: str | None = None
	suffix: str | None = " %"

	@classmethod
	def fixed(cls, count: int):
		return cls(min_integer_digits = 1, decimal_places = count, min_decimal_places = count)

@dataclasses.dataclass(eq = True, frozen = True)
class DataStyleDateTime(DataStyle):
	parts: tuple[str]

	@classmethod
	def isoformat(cls):
		return cls(parts = ("%Y", "-", "%m", "-", "%d", " ", "%H", ":", "%M", ":", "%S"))


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
