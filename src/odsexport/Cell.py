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

import functools
import dataclasses
from .Enums import CellValueType
from .Style import CellStyle, BorderStyle
from .CellRange import CellRange

@dataclasses.dataclass
class Formula():
	value: str | Expression
	value_type: CellValueType = CellValueType.Float

class Cell():
	def __init__(self, sheet: "Sheet", position: tuple[int, int]):
		self._sheet = sheet
		self._position = position
		self._content = None
		self._style = None
		self._conditional_format_class = None
		self._is_covered = False

	@property
	def sheet(self):
		return self._sheet

	@property
	def position(self):
		return self._position

	@property
	def x(self):
		return self.position[0]

	@property
	def y(self):
		return self.position[1]

	@property
	def content(self):
		return self._content

	@content.setter
	def content(self, value):
		if self._is_covered:
			raise ValueError("Cell \"{self}\" of sheet {self.sheet.name} is covered and its value cannot be set.")
		self._content = value

	@property
	def current_style(self):
		return self._style

	@property
	def conditional_format_class(self) -> str | None:
		return self._conditional_format_class

	@conditional_format_class.setter
	def conditional_format_class(self, format_class: str | None):
		self._conditional_format_class = format_class

	@property
	def is_covered(self):
		return self._is_covered

	@functools.cached_property
	def cell_id(self):
		return CellRange(self)

	def make_covered(self):
		self._is_covered = True
		self._content = None
		self._style = None
		self._conditional_format_class = None

	@property
	def left(self):
		return self.rel(x_offset = -1)

	@property
	def right(self):
		return self.rel(x_offset = 1)

	@property
	def up(self):
		return self.rel(y_offset = -1)

	@property
	def down(self):
		return self.rel(y_offset = 1)

	def rel(self, x_offset: int = 0, y_offset: int = 0):
		(x, y) = self._position
		return self._sheet[(x + x_offset, y + y_offset)]

	def clear(self):
		self.content = None
		return self

	def set(self, content: None | str | int | float | Formula):
		self.content = content
		return self

	def set_formula(self, formula_content: str | Expression, value_type = CellValueType.Float):
		self.content = Formula(value = formula_content, value_type = value_type)
		return self

	def style(self, style: "CellStyle | BorderStyle"):
		if isinstance(style, CellStyle):
			return self.style_cell(style)
		elif isinstance(style, BorderStyle):
			return self.style_border(style)
		else:
			raise TypeError(f"Unknown style type: {style}")

	def style_cell(self, cell_style: "CellStyle"):
		self._style = cell_style
		return self

	def style_border(self, border_style: "BorderStyle"):
		if self.current_style is None:
			self.style(CellStyle())
		self.style(dataclasses.replace(self.current_style, border = border_style))
		return self

	def make_range(self, width: int = 1, height: int = 1):
		assert(width != 0)
		assert(height != 0)
		x_offset = (width - 1) if (width > 0) else (width + 1)
		y_offset = (height - 1) if (height > 0) else (height + 1)
		last_cell = self.rel(x_offset = x_offset, y_offset = y_offset)
		return CellRange(self, last_cell)

	def __format__(self, format_string: str):
		return self.cell_id.__format__(format_string)

	def __eq__(self, other):
		return (self.sheet.name, self.position) == (other.sheet.name, other.position)

	def __lt__(self, other):
		return (self.sheet.name, self.position) < (other.sheet.name, other.position)

	def __repr__(self):
		return format(self)
