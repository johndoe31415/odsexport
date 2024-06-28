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

import re
import enum
import string
from .Cell import Cell
from .Style import BorderStyle

class SheetWriter():
	class Mode(enum.IntEnum):
		Row = enum.auto()
		Column = enum.auto()

	def __init__(self, start_cell: "Cell", mode: "Mode" = Mode.Row):
		self._sheet = start_cell.sheet
		self._initial_position = tuple(start_cell.position)
		self._position = list(start_cell.position)
		self._last_cursor = None
		self._mode = mode

	@property
	def cursor(self):
		return self._sheet[tuple(self._position)]

	@cursor.setter
	def cursor(self, cell: "Cell"):
		"""Current cursor, i.e., next cell data will be written to."""
		self._initial_position = tuple(cell.position)
		self._position = list(cell.position)
		self._last_cursor = None

	@property
	def mode(self):
		return self._mode

	@mode.setter
	def mode(self, mode: "Mode"):
		self._mode = mode

	@property
	def last_cursor(self):
		"""Last cursor that was written data to (i.e., not affected by
		'advance' operation)."""
		return self._last_cursor

	def skip(self):
		"""Skip to next cell in current row/column. Does not affect
		'last_cursor' value."""
		if self._mode == self.Mode.Row:
			self._position[0] += 1
		else:
			self._position[1] += 1
		return self

	def advance(self):
		"""Advance to next row in row mode or to next column in column mode."""
		if self._mode == self.Mode.Row:
			self._position[0] = self._initial_position[0]
			self._position[1] += 1
		else:
			self._position[0] += 1
			self._position[1] = self._initial_position[1]
		return self

	def write(self, *values: str | float, style: "DataStyle | CellStyle | None" = None):
		"""Write some value(s) and style it/them accordingly."""
		for value in values:
			self.cursor.set(value)
			if style is not None:
				self.cursor.style(style)
			self._last_cursor = self.cursor
			self.skip()
		return self

	def write_many(self, values: list[str | float], style: "DataStyle | CellStyle | None" = None):
		"""Write many values without advancing."""
		return self.write(*values, style = style)

	def writerow(self, row: list[str | float], style: "DataStyle | CellStyle | None" = None):
		"""Write a complete row and advance to next row (in row mode) or write
		a complete column and advance to next column (in column mode)."""
		return self.write(*row, style = style).advance()

class Sheet():
	_CELL_IDENTIFIER_RE = re.compile(r"\$?(?P<col>[A-Z]+)\$?(?P<row>\d+)")
	_COL_DICT = { letter: index for (index, letter) in enumerate(string.ascii_uppercase) }

	def __init__(self, doc: "ODSDocument", sheet_name: str):
		self._doc = doc
		self._sheet_name = sheet_name
		self._cells = { }
		self._max_x = 0
		self._max_y = 0
		self._col_style = { }
		self._row_style = { }
		self._conditional_formats = [ ]

	@property
	def doc(self):
		return self._doc

	@property
	def name(self):
		return self._sheet_name

	@property
	def has_styled_columns(self):
		return len(self._col_style) > 0

	@property
	def iter_columns(self):
		for x in range(self._max_x + 1):
			yield self._col_style.get(x)

	@property
	def conditional_formats(self):
		return self._conditional_formats

	@property
	def iter_rows(self):
		for y in range(self._max_y + 1):
			yield self._row_style.get(y)

	def style_column(self, x: int, style: "ColStyle"):
		self._col_style[x] = style
		return self

	def style_row(self, y: int, style: "RowStyle"):
		self._row_style[y] = style
		return self

	def style_range(self, cell_range: "CellRange", style: "CellStyle"):
		for position in cell_range:
			self[position.position].style(style)
		return self

	def style_box(self, cell_range: "CellRange", line_style: "LineStyle"):
		for position in cell_range:
			border_style = BorderStyle(
					top = line_style if position.top else None,
					bottom = line_style if position.bottom else None,
					left = line_style if position.left else None,
					right = line_style if position.right else None)
			self[position.position].style_border(border_style)
		return self

	def apply_conditional_format(self, conditional_format: "ConditionalFormat"):
		self._conditional_formats.append(conditional_format)

	def writer(self, start_cell: Cell = None, mode: "Mode" = SheetWriter.Mode.Row):
		if start_cell is None:
			start_cell = self[(0, 0)]
		return SheetWriter(start_cell, mode = mode)

	def _parse_cell_position(self, cell_position_str: str):
		rematch = self._CELL_IDENTIFIER_RE.fullmatch(cell_position_str)
		if rematch is None:
			raise ValueError(f"Not a valid cell identifier: {cell_position_str}")
		rematch = rematch.groupdict()

		x = 0
		for char in rematch["col"]:
			x = (x * 26) + self._COL_DICT[char]
		for i in range(1, len(rematch["col"])):
			x += 26 ** i
		y = int(rematch["row"]) - 1
		return (x, y)

	def __getitem__(self, position: tuple[int, int] | str):
		if isinstance(position, str):
			position = self._parse_cell_position(position)

		(x, y) = position
		self._max_x = max(x, self._max_x)
		self._max_y = max(y, self._max_y)
		if position not in self._cells:
			self._cells[position] = Cell(self, position)
		return self._cells[position]
