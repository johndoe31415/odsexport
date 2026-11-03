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

import zipfile
import xml.dom.minidom
from odsexport.XMLNode import XMLNode
from odsexport.Namespaces import Namespaces

class Tools():
	@classmethod
	def get_unified_namespaces(cls):
		all_namespaces = { }
		for (filename, content) in Namespaces.items():
			for (shortcut, uri) in content.items():
				if (shortcut in all_namespaces) and (all_namespaces[shortcut] != uri):
					raise ValueError(f"Namespace '{shortcut}' means different things in different contexts.")
				all_namespaces[shortcut] = uri
		return all_namespaces

	@classmethod
	def read_xml_from_ods(cls, zip_filename: str, xml_filename: str, normalize_namespaces: bool = True, sort_attributes: bool = True):
		with zipfile.ZipFile(zip_filename, "r") as f:
			xml_data = f.read(xml_filename)
		document = xml.dom.minidom.parseString(xml_data)
		if normalize_namespaces:
			XMLNode.normalize_namespaces(document, cls.get_unified_namespaces())
		if sort_attributes:
			XMLNode(document).sort_attributes_recursively()
		XMLNode.remove_text_whitespace(document)
		pretty_xml = document.toprettyxml(indent = "\t")
		return pretty_xml
