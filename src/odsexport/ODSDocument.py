#	odsexport - Python-native ODS writer library
#	Copyright (C) 2024-2025 Johannes Bauer
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

import io
import collections
from .Sheet import Sheet
from .ODSWriter import ODSWriter
from .Exceptions import DuplicateNameException

class ODSDocument():
	def __init__(self):
		self._sheets = collections.OrderedDict()

	@property
	def sheets(self):
		return iter(self._sheets.values())

	def new_sheet(self, sheet_name: str):
		if sheet_name in self._sheets:
			raise DuplicateNameException(f"Duplicate sheet name: {sheet_name}")
		sheet = Sheet(doc = self, sheet_name = sheet_name)
		self._sheets[sheet_name] = sheet
		return sheet

	def write(self, filename: str):
		ods_writer = ODSWriter(self)
		ods_writer.write(filename)

	def __bytes__(self):
		ods_writer = ODSWriter(self)
		f = io.BytesIO()
		ods_writer.write_stream(f)
		return f.getvalue()
