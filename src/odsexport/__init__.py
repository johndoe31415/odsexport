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

"""
Python-native ODS writer library

This quick start guide will create a new document with a single worksheet that
just contains simple data.

	import odsexport
	doc = odsexport.ODSDocument()
	sheet = doc.new_sheet("My Worksheet")
	writer = sheet.writer()
	writer.writerow([ "Name", "Hometown", "Weight/kg" ], style = odsexport.CellStyle(font = odsexport.Font(bold = True)))
	writer.writerow([ "Joe", "Springfield", "123" ])
	writer.writerow([ "Jack", "St. Louis", "89" ])
	writer.writerow([ "Jill", "New York", "70" ])
	doc.write("my_first_document.ods")

For a more sophisticated example, check out the file write_example_document.py
in the odsexport documentation at https://github.com/johndoe31415/odsexport
"""

from .Enums import HAlign, VAlign, ConditionType
from .Style import Font, DataStyleNumber, DataStylePercent, DataStyleDateTime, CellStyle, RowStyle, ColStyle, BorderStyle, LineStyle, ConditionalFormat, FormatCondition, DataTable
from .Formula import Expression, CellRef, Function
from .CellRange import CellRange
from .ODSDocument import ODSDocument
from .Sheet import SheetWriter

VERSION = "0.1.0"
