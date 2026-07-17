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
import zipfile
import datetime
import collections
import xml.dom.minidom
import odsexport
from .XMLNode import XMLNode
from .Cell import Formula
from .Enums import ConditionType
from .Style import DataStyleNumber, DataStylePercent, DataStyleDateTime
from .Namespaces import Namespaces

class ODSWriter():
	_ODF_VERSION = "1.4"

	def __init__(self, doc: "ODSDocument"):
		self._doc = doc
		self._xml_docs = {
			"styles.xml":				self.__new_styles_doc(),
			"content.xml":				self.__new_content_doc(),
			"meta.xml":					self.__new_meta_doc(),
			"META-INF/manifest.xml":	self.__new_manifest_doc(),
		}
		self._style_ids = { }
		self._counters = collections.defaultdict(int)
		self._used_fonts = set()
		self._serialize()

	@functools.cached_property
	def styles_document(self):
		return self._xml_docs["styles.xml"]

	@functools.cached_property
	def content_document(self):
		return self._xml_docs["content.xml"]

	@functools.cached_property
	def meta_document(self):
		return self._xml_docs["meta.xml"]

	@functools.cached_property
	def manifest_document(self):
		return self._xml_docs["META-INF/manifest.xml"]

	@functools.cached_property
	def content_body(self):
		return XMLNode(XMLNode(self.content_document.childNodes[0]).get_first_child_with_tag("office:body")).get_first_child_with_tag("office:spreadsheet")

	@functools.cached_property
	def content_automatic_styles(self):
		return XMLNode(self.content_document.childNodes[0]).get_first_child_with_tag("office:automatic-styles")

	@functools.cached_property
	def content_font_face_decls(self):
		return XMLNode(self.content_document.childNodes[0]).get_first_child_with_tag("office:font-face-decls")

	@functools.cached_property
	def styles(self):
		return XMLNode(self.styles_document.childNodes[0]).get_first_child_with_tag("office:styles")

	@functools.cached_property
	def meta(self):
		return XMLNode(self.meta_document.childNodes[0]).get_first_child_with_tag("office:meta")

	@classmethod
	def __new_styles_doc(cls):
		styles_doc = xml.dom.minidom.Document()
		styles = styles_doc.appendChild(styles_doc.createElement("office:document-styles"))
		for (nsname, nsuri) in Namespaces["styles.xml"].items():
			styles.setAttributeNS("xmlns", f"xmlns:{nsname}", nsuri)
		styles.setAttributeNS("office", "office:version", cls._ODF_VERSION)
		styles = styles.appendChild(styles_doc.createElement("office:styles"))
		return styles_doc

	@classmethod
	def __new_content_doc(cls):
		content_doc = xml.dom.minidom.Document()
		content = content_doc.appendChild(content_doc.createElement("office:document-content"))
		for (nsname, nsuri) in Namespaces["content.xml"].items():
			content.setAttributeNS("xmlns", f"xmlns:{nsname}", nsuri)
		content.setAttributeNS("office", "office:version", cls._ODF_VERSION)

		font_face_decls = content.appendChild(content_doc.createElement("office:font-face-decls"))
		auto_styles = content.appendChild(content_doc.createElement("office:automatic-styles"))
		body = content.appendChild(content_doc.createElement("office:body"))
		spreadsheet = body.appendChild(content_doc.createElement("office:spreadsheet"))
		return content_doc

	@classmethod
	def __new_meta_doc(cls):
		meta_doc = xml.dom.minidom.Document()
		doc_meta = meta_doc.appendChild(meta_doc.createElement("office:document-meta"))
		for (nsname, nsuri) in Namespaces["meta.xml"].items():
			doc_meta.setAttributeNS("xmlns", f"xmlns:{nsname}", nsuri)
		doc_meta.setAttributeNS("office", "office:version", cls._ODF_VERSION)

		meta = doc_meta.appendChild(meta_doc.createElement("office:meta"))
		return meta_doc

	@classmethod
	def __new_manifest_doc(cls):
		manifest_doc = xml.dom.minidom.Document()
		manifest = manifest_doc.appendChild(manifest_doc.createElement("manifest:manifest"))
		for (nsname, nsuri) in Namespaces["manifest.xml"].items():
			manifest.setAttributeNS("xmlns", f"xmlns:{nsname}", nsuri)
		manifest.setAttributeNS("manifest", "manifest:version", cls._ODF_VERSION)

		XMLNode(manifest.appendChild(manifest_doc.createElement("manifest:file-entry"))).set_ns_attributes("manifest", {
			"full-path":	"/",
			"version":		cls._ODF_VERSION,
			"media-type":	"application/vnd.oasis.opendocument.spreadsheet",
		})
		XMLNode(manifest.appendChild(manifest_doc.createElement("manifest:file-entry"))).set_ns_attributes("manifest", {
			"full-path":	"content.xml",
			"media-type":	"text/xml",
		})
		XMLNode(manifest.appendChild(manifest_doc.createElement("manifest:file-entry"))).set_ns_attributes("manifest", {
			"full-path":	"styles.xml",
			"media-type":	"text/xml",
		})
		XMLNode(manifest.appendChild(manifest_doc.createElement("manifest:file-entry"))).set_ns_attributes("manifest", {
			"full-path":	"meta.xml",
			"media-type":	"text/xml",
		})
		return manifest_doc

	def next_counter(self, name: str):
		value = self._counters[name]
		self._counters[name] += 1
		return value

	def _style_id(self, style_object: object, create_hook: "callable", object_prefix: str = "auto"):
		key = (object_prefix, style_object)
		create_style = key not in self._style_ids
		if create_style:
			self._style_ids[key] = len(self._style_ids)
		style_class_name = f"{object_prefix}{self._style_ids[key]}"
		if create_style:
			create_hook(style_object, style_class_name)
		return style_class_name

	def _create_style_node(self, style_class_name: str, style_class_family: str, parent_node: "Element"):
		style_node = parent_node.appendChild(parent_node.ownerDocument.createElement("style:style"))
		style_node.setAttributeNS("style", "style:name", style_class_name)
		style_node.setAttributeNS("style", "style:display-name", style_class_name)
		style_node.setAttributeNS("style", "style:family", style_class_family)
		return style_node

	def _serialize_row_style(self, row_style: "RowStyle", style_class_name: str):
		style_node = self._create_style_node(style_class_name, "table-row", self.content_automatic_styles)
		property_node = style_node.appendChild(self.content_document.createElement("style:table-row-properties"))
		if row_style.height is not None:
			property_node.setAttributeNS("style", "style:row-height", row_style.height)

	def _serialize_col_style(self, col_style: "ColStyle", style_class_name: str):
		style_node = self._create_style_node(style_class_name, "table-column", self.content_automatic_styles)
		property_node = style_node.appendChild(self.content_document.createElement("style:table-column-properties"))
		if col_style.width is not None:
			property_node.setAttributeNS("style", "style:column-width", col_style.width)

	def _serialize_data_style(self, data_style: "DataStyle", style_class_name: str):
		if isinstance(data_style, (DataStyleNumber, DataStylePercent)):
			style_type = "number" if isinstance(data_style, DataStyleNumber) else "percentage"
			style_node = self.styles.appendChild(self.styles_document.createElement(f"number:{style_type}-style"))
			style_node.setAttributeNS("style", "style:name", style_class_name)

			if data_style.prefix is not None:
				text = style_node.appendChild(style_node.ownerDocument.createElement("number:text"))
				text.appendChild(style_node.ownerDocument.createTextNode(data_style.prefix))

			number_node = style_node.appendChild(self.styles_document.createElement("number:number"))
			if data_style.decimal_places is not None:
				number_node.setAttributeNS("number", "number:decimal-places", str(data_style.decimal_places))
			if data_style.min_decimal_places is not None:
				number_node.setAttributeNS("number", "number:min-decimal-places", str(data_style.min_decimal_places))
			if data_style.min_integer_digits is not None:
				number_node.setAttributeNS("number", "number:min-integer-digits", str(data_style.min_integer_digits))

			if data_style.suffix is not None:
				text = style_node.appendChild(style_node.ownerDocument.createElement("number:text"))
				text.appendChild(style_node.ownerDocument.createTextNode(data_style.suffix))
		elif isinstance(data_style, DataStyleDateTime):
			style_node = self.styles.appendChild(self.styles_document.createElement("number:date-style"))
			style_node.setAttributeNS("style", "style:name", style_class_name)
			style_node.setAttributeNS("number", "number:automatic-order", "true")
			style_node.setAttributeNS("number", "number:format-source", "language")
			for part in data_style.parts:
				match part:
					case "%Y":
						style_node.appendChild(style_node.ownerDocument.createElement("number:year")).setAttributeNS("number", "number:style", "long")

					case "%m":
						style_node.appendChild(style_node.ownerDocument.createElement("number:month")).setAttributeNS("number", "number:style", "long")

					case "%d":
						style_node.appendChild(style_node.ownerDocument.createElement("number:day")).setAttributeNS("number", "number:style", "long")

					case "%H":
						style_node.appendChild(style_node.ownerDocument.createElement("number:hours")).setAttributeNS("number", "number:style", "long")

					case "%M":
						style_node.appendChild(style_node.ownerDocument.createElement("number:minutes")).setAttributeNS("number", "number:style", "long")

					case "%S":
						style_node.appendChild(style_node.ownerDocument.createElement("number:seconds")).setAttributeNS("number", "number:style", "long")

					case _:
						style_node.appendChild(style_node.ownerDocument.createElement("number:text")).appendChild(style_node.ownerDocument.createTextNode(part))
		else:
			raise ValueError(f"Unknown data style class passed of type {type(data_style)}: {data_style}")

	def _serialize_cell_style(self, style: "CellStyle", style_class_name: str, style_node: "Element"):
		if style.data_style is not None:
			style_node.setAttributeNS("style", "style:data-style-name", self._style_id(style.data_style, self._serialize_data_style))

		if (style.rotation_angle is not None) or style.wrap or (style.valign is not None) or (style.background_color is not None) or (style.border is not None):
			table_cell_properties = style_node.appendChild(style_node.ownerDocument.createElement("style:table-cell-properties"))
			if style.rotation_angle is not None:
				table_cell_properties.setAttributeNS("style", "style:rotation-angle", str(style.rotation_angle))
			if style.wrap:
				table_cell_properties.setAttributeNS("fo", "fo:wrap-option", "wrap")
			if style.valign is not None:
				table_cell_properties.setAttributeNS("style", "style:vertical-align", style.valign.value)
			if style.background_color is not None:
				table_cell_properties.setAttributeNS("fo", "fo:background-color", style.background_color)
			if style.border is not None:
				if style.border.top is not None:
					table_cell_properties.setAttributeNS("fo", "fo:border-top", style.border.top.style_str)
				if style.border.bottom is not None:
					table_cell_properties.setAttributeNS("fo", "fo:border-bottom", style.border.bottom.style_str)
				if style.border.left is not None:
					table_cell_properties.setAttributeNS("fo", "fo:border-left", style.border.left.style_str)
				if style.border.right is not None:
					table_cell_properties.setAttributeNS("fo", "fo:border-right", style.border.right.style_str)

		if style.halign is not None:
			paragraph_properties = style_node.appendChild(style_node.ownerDocument.createElement("style:paragraph-properties"))
			paragraph_properties.setAttributeNS("fo", "fo:text-align", style.halign.value)

		if style.font is not None:
			font = style_node.appendChild(style_node.ownerDocument.createElement("style:text-properties"))
			if style.font.name is not None:
				font.setAttributeNS("style", "style:font-name", style.font.name)
				if style.font.name not in self._used_fonts:
					self._used_fonts.add(style.font.name)
					font_face = self.content_font_face_decls.appendChild(self.content_document.createElement("style:font-face"))
					font_face.setAttributeNS("style", "style:name", style.font.name)
					font_face.setAttributeNS("svg", "svg:font-family", f"'{style.font.name}'")

			if style.font.size_pt is not None:
				font.setAttributeNS("fo", "fo:font-size", f"{style.font.size_pt}pt")
			if style.font.bold:
				font.setAttributeNS("fo", "fo:font-weight", "bold")
			if style.font.italic:
				font.setAttributeNS("fo", "fo:font-style", "italic")
			if style.font.color:
				font.setAttributeNS("fo", "fo:color", style.font.color)
		return style

	def _serialize_automatic_cell_style(self, style: "CellStyle", style_class_name: str):
		style_node = self._create_style_node(style_class_name, "table-cell", self.content_automatic_styles)
		return self._serialize_cell_style(style, style_class_name, style_node)

	def _serialize_global_cell_style(self, style: "CellStyle", style_class_name: str):
		style_node = self._create_style_node(style_class_name, "table-cell", self.styles)
		return self._serialize_cell_style(style, style_class_name, style_node)

	def _serialize_default_styles(self):
		# These are styles that are empty. They are needed because Excel when
		# importing ODS requires a table-row tag to contain a style:name
		# attribute otherwise it will ignore That the row should be collapsed.
		# Since they are very small, we always generate these definitions even
		# if they're never used.
		self._create_style_node("dr", "table-row", self.content_automatic_styles)
		self._create_style_node("dc", "table-column", self.content_automatic_styles)

	def _serialize_cell(self, cell: "Cell", cell_node: "Element", merged_range: CellRange | None):
		if merged_range is not None:
			cell_node.setAttributeNS("table", "table:number-columns-spanned", str(merged_range.width))
			cell_node.setAttributeNS("table", "table:number-rows-spanned", str(merged_range.height))
		if cell.conditional_format_class is not None:
			cell_node.setAttributeNS("table", "table:style-name", cell.conditional_format_class)
		elif cell.current_style is not None:
			cell_node.setAttributeNS("table", "table:style-name", self._style_id(cell.current_style, self._serialize_automatic_cell_style))

		if cell.content is None:
			return

		if isinstance(cell.content, str):
			cell_node.setAttributeNS("office", "office:value-type", "string")
			text_node = cell_node.appendChild(cell_node.ownerDocument.createElement("text:p"))
			text_node.appendChild(cell_node.ownerDocument.createTextNode(cell.content))
		elif isinstance(cell.content, (int, float)):
			cell_node.setAttributeNS("office", "office:value-type", "float")
			cell_node.setAttributeNS("office", "office:value", str(cell.content))
			text_node = cell_node.appendChild(cell_node.ownerDocument.createElement("text:p"))
			text_node.appendChild(cell_node.ownerDocument.createTextNode(str(cell.content)))
		elif isinstance(cell.content, Formula):
			cell_node.setAttributeNS("office", "office:value-type", "error")
			if isinstance(cell.content.value, str):
				formula_str = cell.content.value
			else:
				if not hasattr(cell.content.value, "render"):
					raise ValueError(f"Formula value has unrenderable type \"{type(cell.content.value).__name__}\" in cell {cell} of \"{cell.sheet.name}\": {cell.content.value}")
				formula_str = cell.content.value.render(cell.sheet)
			cell_node.setAttributeNS("table", "table:formula", f"of:={formula_str}")
		elif isinstance(cell.content, datetime.datetime):
			cell_node.setAttributeNS("office", "office:value-type", "date")
			cell_node.setAttributeNS("office", "office:date-value", cell.content.strftime("%Y-%m-%dT%H:%M:%S"))
		else:
			raise ValueError(f"Unknown cell type of class \"{type(cell.content).__name__}\" in cell {cell} of \"{cell.sheet.name}\": {cell.content}")

	def _serialize_sheet(self, sheet: "Sheet"):
		table_node = self.content_body.appendChild(self.content_document.createElement("table:table"))
		table_node.setAttributeNS("table", "table:name", sheet.name)

		for col_style in sheet.iter_columns:
			col_node = table_node.appendChild(self.content_document.createElement("table:table-column"))
			if col_style is not None:
				if col_style.hidden:
					col_node.setAttributeNS("table", "table:visibility", "collapse")
				if col_style.width is not None:
					col_node.setAttributeNS("table", "table:style-name", self._style_id(col_style, self._serialize_col_style))
				else:
					col_node.setAttributeNS("table", "table:style-name", "dc")

		for (y, row_style) in enumerate(sheet.iter_rows):
			row_node = table_node.appendChild(self.content_document.createElement("table:table-row"))
			if row_style is not None:
				if row_style.hidden:
					row_node.setAttributeNS("table", "table:visibility", "collapse")
				if row_style.height is not None:
					row_node.setAttributeNS("table", "table:style-name", self._style_id(row_style, self._serialize_row_style))
				else:
					row_node.setAttributeNS("table", "table:style-name", "dr")
			for x in range(sheet._max_x + 1):
				cell = sheet._cells.get((x, y))
				cell_tag = "table:covered-table-cell" if ((cell is not None) and cell.is_covered) else "table:table-cell"
				cell_node = row_node.appendChild(self.content_document.createElement(cell_tag))
				merged_range = sheet.get_merged_range((x, y))		# The CellRange if this is the top left cell of a merged range
				if cell is not None:
					# Regular cell or covered cell
					self._serialize_cell(cell, cell_node, merged_range)
				else:
					# Non-existent cell/empty
					cell_node.setAttributeNS("office", "office:value-type", "string")
					text_node = cell_node.appendChild(cell_node.ownerDocument.createElement("text:p"))
					text_node.appendChild(cell_node.ownerDocument.createTextNode(""))

	def _serialize_database_ranges(self, sheets: "Iterator[Sheet]"):
		data_tables = [ ]
		for sheet in sheets:
			data_tables += sheet.data_tables

		if len(data_tables) == 0:
			return

		database_ranges_node = self.content_body.appendChild(self.content_document.createElement("table:database-ranges"))
		for data_table in data_tables:
			database_range_node = database_ranges_node.appendChild(self.content_document.createElement("table:database-range"))
			database_range_node.setAttributeNS("table", "table:name", f"__datatbl_{self.next_counter('data_table')}")
			database_range_node.setAttributeNS("table", "table:target-range-address", format(data_table.cell_range, "a"))
			database_range_node.setAttributeNS("table", "table:display-filter-buttons", "true")

	def _serialize_conditional_formatting_styles(self, sheets: "Iterator[Sheet]"):
		cond_id = 0
		for sheet in sheets:
			for conditional_format in sheet.conditional_formats:
				conditional_format_styles = { }
				for cell in conditional_format.target.iter_cells(sheet):
					if cell.current_style not in conditional_format_styles:
						conditional_format_class = f"cond{cond_id}_{len(conditional_format_styles)}"
						conditional_format_styles[cell.current_style] = conditional_format_class
					else:
						conditional_format_class = conditional_format_styles[cell.current_style]
					cell.conditional_format_class = conditional_format_class

				for (parent_style, conditional_format_class) in conditional_format_styles.items():
					style_node = self._create_style_node(conditional_format_class, "table-cell", self.content_automatic_styles)
					if (parent_style is not None) and (parent_style.data_style is not None):
						style_node.setAttributeNS("style", "style:data-style-name", self._style_id(parent_style.data_style, self._serialize_data_style))
					for condition in conditional_format.conditions:
						cond_node = style_node.appendChild(self.content_document.createElement("style:map"))
						cond_node.setAttributeNS("style", "style:apply-style-name", self._style_id(condition.cell_style, self._serialize_global_cell_style, object_prefix = "glbl"))
						if conditional_format.condition_type == ConditionType.CellValue:
							cond_node.setAttributeNS("style", "style:condition", f"cell-content(){condition.condition}")
						elif conditional_format.condition_type == ConditionType.Formula:
							cond_node.setAttributeNS("style", "style:condition", f"is-true-formula({condition.condition})")
						else:
							raise TypeError(f"Unknown type: {condition.condition.type}")
						base_cell = conditional_format.base_cell if (conditional_format.base_cell is not None) else conditional_format.target.src
						cond_node.setAttributeNS("style", "style:base-cell-address", format(base_cell, "a"))

				cond_id += 1

	def _serialize_metadata(self):
		now = datetime.datetime.now()
		metadata = {
			"meta:generator":		f"https://github.com/johndoe31415/odsexport v{odsexport.VERSION}",
			"meta:creation-date":	now.strftime("%Y-%m-%dT%H:%M:%S"),
			"dc:date":				now.strftime("%Y-%m-%dT%H:%M:%S"),
		}
		for (key, value) in metadata.items():
			node = self.meta.appendChild(self.meta_document.createElement(key))
			node.appendChild(self.meta_document.createTextNode(value))

	def _serialize(self):
		self._serialize_metadata()
		self._serialize_conditional_formatting_styles(self._doc.sheets)
		self._serialize_default_styles()
		for sheet in self._doc.sheets:
			self._serialize_sheet(sheet)
		self._serialize_database_ranges(self._doc.sheets)

	def write_stream(self, f):
		with zipfile.ZipFile(f, "w") as zf:
			zf.writestr("mimetype", b"application/vnd.oasis.opendocument.spreadsheet", compress_type = zipfile.ZIP_STORED)
			for (filename, xml_document) in self._xml_docs.items():
				zf.writestr(filename, xml_document.toxml(encoding = "utf-8"), compress_type = zipfile.ZIP_DEFLATED)

	def write(self, filename: str):
		with open(filename, "wb") as f:
			self.write_stream(f)
