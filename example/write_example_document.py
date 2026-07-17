#!/usr/bin/env python3
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

import math
import random
import datetime
import fractions
import odsexport

def create_format_sheet(doc):
	sheet = doc.new_sheet("Formatting")

	sheet[(0, 0)].set("Rotated Arial").style(odsexport.CellStyle(font = odsexport.Font(bold = True, italic = True, size_pt = 9, name = "Arial"), halign = odsexport.HAlign.Left, rotation_angle = 45))
	sheet[(1, 0)].set("Bold only").style(odsexport.CellStyle(font = odsexport.Font(bold = True)))
	sheet[(2, 0)].set("Italics only").style(odsexport.CellStyle(font = odsexport.Font(italic = True)))
	sheet[(3, 0)].set("Left adjust").style(odsexport.CellStyle(halign = odsexport.HAlign.Left))
	sheet[(4, 0)].set("Centered").style(odsexport.CellStyle(halign = odsexport.HAlign.Center))
	sheet[(5, 0)].set("Right adjust").style(odsexport.CellStyle(halign = odsexport.HAlign.Right))
	sheet[(6, 0)].set("Blue text").style(odsexport.CellStyle(font = odsexport.Font(color = "#0000ff")))
	sheet[(7, 0)].set("Blue background").style(odsexport.CellStyle(background_color = "#aaaaff"))

	sheet[(2, 2)].set("Top left corner of red box")
	sheet[(7, 4)].set("Bottom right corner of red box with wrapped text as well because the content in here is so long").style(odsexport.CellStyle(wrap = True))
	cell_range = odsexport.CellRange.parse(sheet, "C3:H5").style_box(odsexport.LineStyle(color = "#ff0000"))

	sheet[(0, 6)].set("Below here is a row that is hidden.")
	sheet.style_row(7, odsexport.RowStyle(hidden = True))
	sheet[(0, 7)].set("I'm hidden!")
	sheet[(0, 8)].set("Above this row is a row that is hidden.")

	sheet[(10, 0)].set("Column right of this is hidden")
	sheet.style_column(11, odsexport.ColStyle(hidden = True))
	sheet[(11, 0)].set("I'm hidden!")
	sheet[(12, 0)].set("Column left of this is hidden")

	sheet["K5"].set("This is K5")
	sheet["AB5"].set("This is AB5")

	sheet[(0, 11)].set("This row is exactly 1cm in height and text is vertically centered.").style(odsexport.CellStyle(valign = odsexport.VAlign.Middle))
	sheet.style_row(11, odsexport.RowStyle(height = "1cm"))
	sheet[(0, 12)].set("This row is exactly 2cm in height and text is vertically centered.").style(odsexport.CellStyle(valign = odsexport.VAlign.Middle))
	sheet.style_row(12, odsexport.RowStyle(height = "2cm"))

	sheet[(0, 14)].set("Value for next sheet:")
	cell = sheet[(1, 14)].set(123.456)
	return cell

def create_formula_sheet(doc, reference_cell):
	sheet = doc.new_sheet("Formulas")
	sheet.style_column(1, odsexport.ColStyle(width = "5cm"))
	bold_style = odsexport.CellStyle(font = odsexport.Font(bold = True))

	sheet.style_column(0, odsexport.ColStyle(width = "4cm"))
	sheet[(0, 0)].set("Imported value:").style(bold_style)
	cell = sheet[(1, 0)].set_formula(odsexport.CellRef(reference_cell))

	left = sheet[(0, 1)].set("Computed value 1:").style(bold_style)
	right = sheet[(1, 1)].set_formula((odsexport.CellRef(cell) * 2 / 3) + 123 + odsexport.Function("Pi"))
	right = sheet[(2, 1)].set_formula(f"({cell:b}*2/3) + 123 + Pi()")	# This can be used, but is discouraged
	cell = right

	left = sheet[(0, 2)].set("Computed value 2:").style(bold_style)
	right = sheet[(1, 2)].set_formula(odsexport.CellRef(cell) / 300)
	cell2 = right

	for num in range(6):
		left = left.down
		right = right.down
		left.set(f"Rounded with {num} digits:").style(bold_style)
		right.set_formula(odsexport.CellRef(cell)).style(odsexport.CellStyle(data_style = odsexport.DataStyleNumber.fixed(num)))

	for num in range(3):
		left = left.down
		right = right.down
		left.set(f"Percent with {num} digits:").style(bold_style)
		right.set_formula(odsexport.CellRef(cell2)).style(odsexport.CellStyle(data_style = odsexport.DataStylePercent.fixed(num)))

	now = datetime.datetime.now()
	left = left.down
	right = right.down
	left.set("Datetime as ISO:").style(bold_style)
	right.set(now).style(odsexport.CellStyle(data_style = odsexport.DataStyleDateTime.isoformat()))

	left = left.down
	right = right.down
	left.set("Datetime as German:").style(bold_style)
	right.set(now).style(odsexport.CellStyle(data_style = odsexport.DataStyleDateTime(parts = ("%d", ".", "%m", ".", "%Y", " ", "%H", ":", "%M"))))

	writer = sheet.writer(left.down.down)
	writer.writerow([ "Radius of cylinder:", 40, "mm" ])
	writer.writerow([ "Height of cylinder:", 120, "mm" ])
	radius_cell = writer.cursor.up.up.right
	height_cell = radius_cell.down
	cylinder_volume = (odsexport.CellRef(radius_cell) ** 2) * 3.1415 * height_cell
	writer.writerow([ "Volume of cylinder:", cylinder_volume, "mm³" ])
	writer.advance()

	writer.writerow([ "Hour value:", 14 ])
	hour_cell = writer.cursor.up.right
	hour_ref = odsexport.CellRef(hour_cell)
	formula = ((hour_ref >= 0) & (hour_ref <= 24)).then("Valid", else_value = "Invalid")
	writer.writerow([ "Hours valid?", formula ])

	writer.cursor.rel(y_offset = -6).make_range(height = 6).style(bold_style)
	writer.cursor.up.right.style(odsexport.CellStyle(halign = odsexport.HAlign.Right))


def create_conditional_formatting_sheet(doc):
	sheet = doc.new_sheet("Conditional Formatting")
	sheet.style_column(1, odsexport.ColStyle(width = "3cm"))
	sheet.style_column(2, odsexport.ColStyle(width = "4cm"))
	for i in range(25):
		data_cell = sheet[(0, i)]
		text1_cell = data_cell.right
		text2_cell = text1_cell.right

		data_cell.set(i)
		text1_cell.set(f"Hexvalue {i:#04x}")
		text2_cell.set(f"Octvalue {i:#08o}")

	# Create a simple conditional format with value-dependent evaluation
	cell_range = odsexport.CellRange(sheet[(0, 0)], sheet[(0, 24)])
	sheet.apply_conditional_format(odsexport.ConditionalFormat(target = cell_range, conditions = (
		odsexport.FormatCondition(condition = "<10", cell_style = odsexport.CellStyle(background_color = "#ff0000")),
		odsexport.FormatCondition(condition = "<20", cell_style = odsexport.CellStyle(background_color = "#0000ff")),
		odsexport.FormatCondition(condition = "<30", cell_style = odsexport.CellStyle(background_color = "#00ff00")),
	)))

	# Create a conditional format with a formula that evaluates relative fields
	# (fixed column mode)
	cell_range = odsexport.CellRange(sheet[(1, 0)], sheet[(1, 24)])
	sheet.apply_conditional_format(odsexport.ConditionalFormat(target = cell_range, condition_type = odsexport.ConditionType.Formula, conditions = (
		odsexport.FormatCondition(condition = f"{cell_range.src.left:acb}<16", cell_style = odsexport.CellStyle(background_color = "#ff0000")),
		odsexport.FormatCondition(condition = f"{cell_range.src.left:acb}<32", cell_style = odsexport.CellStyle(background_color = "#0000ff")),
	)))

	# Create a conditional format with a formula that evaluates relative fields
	# (fixed column mode)
	cell_range = odsexport.CellRange(sheet[(2, 0)], sheet[(2, 24)])
	sheet.apply_conditional_format(odsexport.ConditionalFormat(target = cell_range, condition_type = odsexport.ConditionType.Formula, conditions = (
		odsexport.FormatCondition(condition = f"{cell_range.src.left.left:acb}<8", cell_style = odsexport.CellStyle(background_color = "#ff0000")),
		odsexport.FormatCondition(condition = f"{cell_range.src.left.left:acb}<16", cell_style = odsexport.CellStyle(background_color = "#00ff00")),
		odsexport.FormatCondition(condition = f"{cell_range.src.left.left:acb}<24", cell_style = odsexport.CellStyle(background_color = "#0000ff")),
		odsexport.FormatCondition(condition = f"{cell_range.src.left.left:acb}<32", cell_style = odsexport.CellStyle(background_color = "#00ffff")),
	)))

def create_conditional_formatting_image(doc):
	sheet = doc.new_sheet("Image")
	(width, height) = (16, 16)
	cell_length = "1cm"
	for x in range(width):
		sheet.style_column(x, odsexport.ColStyle(width = cell_length))
	for y in range(height):
		sheet.style_row(y, odsexport.RowStyle(height = cell_length))
	colors = {
		0: "dbd8c4",
		1: "ed1c24",
		2: "f44336",
		3: "4caf50",
		4: "000000",
		5: "ede7f6",
	}
	values = [
		[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 4, 2, 5, 3, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 5, 3, 0],
		[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 5, 3, 0],
		[0, 0, 0, 0, 0, 1, 1, 1, 4, 1, 1, 2, 5, 3, 0, 0],
		[0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 5, 3, 0, 0],
		[0, 0, 2, 2, 4, 1, 1, 1, 1, 1, 2, 5, 3, 0, 0, 0],
		[0, 0, 5, 5, 2, 2, 1, 1, 1, 2, 2, 5, 3, 0, 0, 0],
		[0, 0, 3, 3, 5, 5, 2, 2, 2, 5, 5, 3, 0, 0, 0, 0],
		[0, 0, 0, 0, 3, 3, 5, 5, 5, 3, 3, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	]
	writer = sheet.writer()
	for row in values:
		writer.writerow(row)

	cell_range = odsexport.CellRange(sheet[(0, 0)], sheet[(width - 1, height - 1)])
	conditions = [ ]
	for (index, color) in colors.items():
		conditions.append(odsexport.FormatCondition(condition = f"={index}", cell_style = odsexport.CellStyle(background_color = f"#{color}")))
	sheet.apply_conditional_format(odsexport.ConditionalFormat(target = cell_range, conditions = conditions))

def create_conditional_formatting_multi_format(doc):
	sheet = doc.new_sheet("Conditional Multi-Format")
	writer = sheet.writer()
	writer.writerow([ "1 Decimal", "3 Decimals", "% 1 Dec", "% 2 Dec" ])
	range_start = writer.cursor
	for x in range(1, 20):
		writer.write(70 * math.sin(x), style = odsexport.CellStyle(data_style = odsexport.DataStyleNumber.fixed(1)))
		writer.write(math.sin(10 * x), style = odsexport.CellStyle(data_style = odsexport.DataStyleNumber.fixed(3)))
		writer.write(math.sin(x + 4) % 2, style = odsexport.CellStyle(data_style = odsexport.DataStylePercent.fixed(1)))
		writer.write(math.sin(x + 5) % 0.4, style = odsexport.CellStyle(data_style = odsexport.DataStylePercent.fixed(2)))
		range_end = writer.cursor.left
		writer.advance()

	cell_range = odsexport.CellRange(range_start, range_end)
	sheet.apply_conditional_format(odsexport.ConditionalFormat(target = cell_range, condition_type = odsexport.ConditionType.Formula, conditions = (
		odsexport.FormatCondition(condition = f"{cell_range.src:cb}<-10", cell_style = odsexport.CellStyle(background_color = "#ff0000")),
		odsexport.FormatCondition(condition = f"{cell_range.src:cb}>10", cell_style = odsexport.CellStyle(background_color = "#00ff00")),
	)))

def create_simple_sheet(doc):
	sheet = doc.new_sheet("Simple row-writer")
	writer = sheet.writer()
	writer.writerow([ "Value", "Pi*Value", "Hex", "Formula" ])
	for i in range(10):
		cell = sheet[f"B{i+2}"]
		row = [ i, i * 3.1415, f"{i:#04x}", (odsexport.CellRef(cell) + 2) * 4 ]
		writer.writerow(row)

def create_internal_function_sheet(doc):
	sheet = doc.new_sheet("Symmetric rounding")
	writer = sheet.writer()
	writer.writerow([ "Value", "Excel ROUND", "Python float round()", "Python exact round()", "odsexport round()", "Difference", "OK?" ])
	for i in range(121):
		value = (i - 60) / 100
		exact_value = fractions.Fraction(i - 60, 100)
		writer.write(value)

		cellref = odsexport.CellRef(writer.last_cursor)
		writer.write(cellref.round(1))
		writer.write(round(value, 1))
		writer.write(float(round(exact_value, 1)))
		writer.write(round(cellref, 1))
		writer.write(odsexport.CellRef(writer.last_cursor.left) - writer.last_cursor)
		writer.write((odsexport.CellRef(writer.last_cursor) != 0).then("ERROR", else_value = ""))
		writer.advance()

def create_data_table(doc):
	sheet = doc.new_sheet("Data table")
	writer = sheet.writer()

	last_names = [ "Smith", "Johnson", "Williams", "Brown", "Jones", "Rodriguez", "Miller", "Davis" ]
	first_names = [ "Mary", "Patricia", "Linda", "Emma", "Jacob", "Michael", "Thomas" ]
	adjectives = [ "Brown", "Yellow", "Pink", "Fast", "Ugly" ]
	team_nouns = [ "Bears", "Turds", "Skunks", "Flamingos" ]

	writer.writerow([ "Last name", "First name", "Team", "Score" ])
	for _ in range(100):
		writer.writerow([ random.choice(last_names), random.choice(first_names), f"{random.choice(adjectives)} {random.choice(team_nouns)}", random.randint(0, 50) ])

	cell_range = odsexport.CellRange(writer.initial_cursor, writer.last_cursor)
	sheet.add_data_table(odsexport.DataTable(cell_range = cell_range))

	data_range = cell_range.sub_range(x_offset = 3, y_offset = 1, height = -1, width = 1)

	writer.cursor = writer.cursor.rel(x_offset = 2, y_offset = 1)
	data_range = odsexport.CellRef(data_range)
	writer.writerow([ "Average unless no data:", data_range.average_unless_no_data() ])
	writer.writerow([ "Average:", data_range.average() ])
	writer.writerow([ "Sum:", data_range.sum() ])
	writer.writerow([ "Min:", data_range.min() ])
	writer.writerow([ "Max:", data_range.max() ])

doc = odsexport.ODSDocument()
reference_cell = create_format_sheet(doc)
create_formula_sheet(doc, reference_cell)
create_conditional_formatting_sheet(doc)
create_conditional_formatting_image(doc)
create_conditional_formatting_multi_format(doc)
create_simple_sheet(doc)
create_internal_function_sheet(doc)
create_data_table(doc)
doc.write("example_document.ods")
