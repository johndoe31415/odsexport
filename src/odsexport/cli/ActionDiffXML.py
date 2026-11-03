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
import subprocess
import tempfile
import xml.dom.minidom
from odsexport.XMLNode import XMLNode
from odsexport.Namespaces import Namespaces
from .MultiCommand import BaseAction

class ActionDiffXML(BaseAction):
	def _read_xml(self, zip_filename: str):
		with zipfile.ZipFile(zip_filename, "r") as f:
			xml_data = f.read(self._xml_filename)
		document = xml.dom.minidom.parseString(xml_data)
		if not self._args.no_namespace_normalization:
			XMLNode.normalize_namespaces(document, Namespaces[self._xml_filename])
		if not self._args.no_attribute_sort:
			XMLNode(document).sort_attributes_recursively()
		XMLNode.remove_text_whitespace(document)
		pretty_xml = document.toprettyxml(indent = "\t")
		return pretty_xml

	def run(self):
		self._xml_filename = "styles.xml" if self.args.style_file else "content.xml"
		xml1 = self._read_xml(self._args.filename1)
		xml2 = self._read_xml(self._args.filename2)
		with tempfile.NamedTemporaryFile(prefix = "odsbutcher_", suffix = ".xml", mode = "w") as f1, tempfile.NamedTemporaryFile(prefix = "odsbutcher_", suffix = ".xml", mode = "w") as f2:
			f1.write(xml1)
			f1.flush()
			f2.write(xml2)
			f2.flush()
			subprocess.run([ "diff", f1.name, f2.name ], check = False)
		return 0
