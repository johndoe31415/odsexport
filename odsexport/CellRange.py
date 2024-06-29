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

import string
import collections
from .Style import BorderStyle

class CellRange():
	CellLocation = collections.namedtuple("CellLocation", [ "position", "top", "bottom", "left", "right" ])

	def __init__(self, src_cell: "Cell", dest_cell: "Cell | None" = None):
		assert((dest_cell is None) or (src_cell.sheet is dest_cell.sheet))
		x = [ src_cell.x ]
		y = [ src_cell.y ]
		if dest_cell is not None:
			x.append(dest_cell.x)
			y.append(dest_cell.y)
		x.sort()
		y.sort()

		(x1, y1) = (min(x), min(y))
		(x2, y2) = (max(x), max(y))

		self._src_cell = src_cell.sheet[(x1, y1)]
		self._dest_cell = src_cell.sheet[(x2, y2)]


	@classmethod
	def parse(cls, sheet: "Sheet", str_definition: str):
		if ":" in str_definition:
			(src_str, dest_str) = str_definition.split(":", maxsplit = 1)
		else:
			src_str = str_definition
			dest_str = str_definition
		return cls(src_cell = sheet[src_str], dest_cell = sheet[dest_str])

	@property
	def src(self):
		return self._src_cell

	@property
	def dest(self):
		return self._dest_cell

	def rel(self, x_offset: int = 0, y_offset: int = 0):
		src = self.src.rel(x_offset = x_offset, y_offset = y_offset)
		dest = self.dest.rel(x_offset = x_offset, y_offset = y_offset)
		return CellRange(src, dest)

	@property
	def width(self):
		return self.dest.x - self.src.x + 1

	@property
	def height(self):
		return self.dest.y - self.src.y + 1

	@staticmethod
	def _col_letter(x):
		letter_count = 0
		offset = 0
		while x >= offset:
			letter_count += 1
			offset += 26 ** letter_count

		x -= offset
		xstr = ""
		for i in range(letter_count):
			xstr = string.ascii_uppercase[x % 26] + xstr
			x //= 26
		return xstr

	@staticmethod
	def _row_number(y):
		return str(y + 1)

	@property
	def is_range(self):
		return self._src_cell != self._dest_cell

	def sub_range(self, x_offset: int = 0, y_offset: int = 0, width: int | None = None, height: int | None = None):
		if width is None:
			new_width = self.width
		elif width > 0:
			new_width = width
		else:
			new_width = self.width + width
		if new_width < 1:
			raise ValueError(f"Width specification failure, new width would be {new_width} cells.")

		if height is None:
			new_height = self.height
		elif height > 0:
			new_height = height
		else:
			new_height = self.height + height
		if new_height < 1:
			raise ValueError(f"Height specification failure, new height would be {new_height} cells.")

		new_src = self.src.rel(x_offset = x_offset, y_offset = y_offset)
		new_dest = new_src.rel(x_offset = new_width - 1, y_offset = new_height - 1)
		return CellRange(new_src, new_dest)

	def style(self, style: "Style"):
		for cell_location in self:
			cell = self.src.sheet[cell_location.position]
			cell.style(style)
		return self

	def style_box(self, line_style: "LineStyle"):
		for cell_location in self:
			border_style = BorderStyle(
					top = line_style if cell_location.top else None,
					bottom = line_style if cell_location.bottom else None,
					left = line_style if cell_location.left else None,
					right = line_style if cell_location.right else None)
			cell = self.src.sheet[cell_location.position]
			cell.style_border(border_style)
		return self

	def __iter__(self):
		(min_x, min_y) = self.src.position
		(max_x, max_y) = self.dest.position

		# Top
		for xoff in range(self.width):
			x = min_x + xoff
			yield self.CellLocation(position = (x, min_y), top = True, bottom = (min_y == max_y), left = (x == min_x), right = (x == max_x))

		# Bottom
		if min_y != max_y:
			for xoff in range(self.width):
				x = min_x + xoff
				yield self.CellLocation(position = (x, max_y), top = False, bottom = True, left = (x == min_x), right = (x == max_x))

		if self.height > 2:
			# Left
			for yoff in range(1, self.height - 1):
				y = min_y + yoff
				yield self.CellLocation(position = (min_x, y), top = False, bottom = False, left = True, right = (min_x == max_x))

			# Right
			if min_x != max_x:
				for yoff in range(1, self.height - 1):
					y = min_y + yoff
					yield self.CellLocation(position = (max_x, y), top = False, bottom = False, left = False, right = True)

	def __format__(self, format_string: str):
		absolute = "a" in format_string
		fixed_col = "c" in format_string
		fixed_row = "r" in format_string

		prefix = f"'{self._src_cell.sheet.name}'." if absolute else ""
		col = "$" if fixed_col else ""
		row = "$" if fixed_row else ""
		if not self.is_range:
			return f"{prefix}{col}{self._col_letter(self._src_cell.x)}{row}{self._row_number(self._src_cell.y)}"
		else:
			return f"{prefix}{col}{self._col_letter(self._src_cell.x)}{row}{self._row_number(self._src_cell.y)}:{prefix}{col}{self._col_letter(self._dest_cell.x)}{row}{self._row_number(self._dest_cell.y)}"

	def __repr__(self):
		return format(self)
