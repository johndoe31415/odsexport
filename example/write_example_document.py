#!/usr/bin/env python3
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

import random
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
	bold_style = odsexport.CellStyle(font = odsexport.Font(bold = True))

	sheet.style_column(0, odsexport.ColStyle(width = "4cm"))
	sheet[(0, 0)].set("Imported value:").style(bold_style)
	cell = sheet[(1, 0)].set_formula(f"{reference_cell:a}")

	left = sheet[(0, 1)].set("Computed value 1:").style(bold_style)
	right = sheet[(1, 1)].set_formula(f"({cell}*2/3) + 123 + Pi()")
	cell = right

	left = sheet[(0, 2)].set("Computed value 2:").style(bold_style)
	right = sheet[(1, 2)].set_formula(f"{cell}/300")
	cell2 = right

	for num in range(6):
		left = left.down
		right = right.down
		left.set(f"Rounded with {num} digits:").style(bold_style)
		right.set_formula(f"{cell}").style(odsexport.CellStyle(data_style = odsexport.DataStyle.fixed_decimal_places(num)))
	for num in range(3):
		left = left.down
		right = right.down
		left.set(f"Percent with {num} digits:").style(bold_style)
		right.set_formula(f"{cell2}").style(odsexport.CellStyle(data_style = odsexport.DataStyle.percent_fixed_decimal_places(num)))

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
	cell_range = odsexport.CellRange(sheet[(0, 0)], sheet[(0, 20)])
	sheet.apply_conditional_format(odsexport.ConditionalFormat(target = cell_range, conditions = (
		odsexport.FormatCondition(condition = "<5", cell_style = odsexport.CellStyle(background_color = "#ff0000")),
		odsexport.FormatCondition(condition = "<10", cell_style = odsexport.CellStyle(background_color = "#0000ff")),
		odsexport.FormatCondition(condition = "<15", cell_style = odsexport.CellStyle(background_color = "#00ff00")),
	)))

	# Create a conditional format with a formula that evaluates relative fields
	# (fixed column mode)
	cell_range = odsexport.CellRange(sheet[(1, 0)], sheet[(2, 20)])
	sheet.apply_conditional_format(odsexport.ConditionalFormat(target = cell_range, condition_type = odsexport.ConditionType.Formula, conditions = (
		odsexport.FormatCondition(condition = f"{cell_range.src.left:ac}<4", cell_style = odsexport.CellStyle(background_color = "#ff0000")),
		odsexport.FormatCondition(condition = f"{cell_range.src.left:ac}<8", cell_style = odsexport.CellStyle(background_color = "#0000ff")),
		odsexport.FormatCondition(condition = f"{cell_range.src.left:ac}<16", cell_style = odsexport.CellStyle(background_color = "#00ff00")),
	)))

def create_simple_sheet(doc):
	sheet = doc.new_sheet("Simple data entry")
	writer = sheet.writer()
	for i in range(10):
		row = [ "Value:", i, i * 3.1415, f"{i:#04x}", odsexport.Formula(f"B{i+1}*4") ]
		writer.writerow(row)

def create_internal_function_sheet(doc):
	sheet = doc.new_sheet("High-level functions")
	writer = sheet.writer()
	writer.writerow([ "Value", "ROUND(x; 1)", "ROUND_HALF_TO_EVEN(x; 1)", "Difference" ])
	for i in range(121):
		value = (i - 60) / 100

		writer.write(value)
		cell = writer.last_cursor

		writer.write(odsexport.Formula(f"ROUND({cell};1)"))
		writer.write(odsexport.Formula(odsexport.Formula.round_half_to_even(cell, 1)))
		writer.write(odsexport.Formula(f"{writer.last_cursor.left}-{writer.last_cursor}"))
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
	writer.writerow([ "Average:", odsexport.Formula(odsexport.Formula.average_when_have_values(data_range, subtotal = True)) ])
	writer.writerow([ "Sum:", odsexport.Formula(odsexport.Formula.sum(data_range, subtotal = True)) ])

doc = odsexport.ODSDocument()
reference_cell = create_format_sheet(doc)
create_formula_sheet(doc, reference_cell)
create_conditional_formatting_sheet(doc)
create_simple_sheet(doc)
create_internal_function_sheet(doc)
create_data_table(doc)
doc.write("example_document.ods")
