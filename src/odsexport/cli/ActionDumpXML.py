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

import os
import zipfile
import tempfile
import subprocess
import xml.dom.minidom
from odsexport.XMLNode import XMLNode
from .MultiCommand import BaseAction
from odsexport.Namespaces import Namespaces

class ActionDumpXML(BaseAction):
	def _confirm(self, prompt: str):
		while True:
			yn = input(prompt)
			if yn in "Yy":
				return True
			elif yn in "Nn":
				return False

	def _read_xml(self):
		with zipfile.ZipFile(self._args.filename, "r") as f:
			xml_data = f.read(self._xml_filename)
		document = xml.dom.minidom.parseString(xml_data)
		if not self._args.no_namespace_normalization:
			XMLNode.normalize_namespaces(document, Namespaces[self._xml_filename])
		if not self._args.no_attribute_sort:
			XMLNode(document).sort_attributes_recursively()
		XMLNode.remove_text_whitespace(document)
		pretty_xml = document.toprettyxml(indent = "\t")
		return pretty_xml

	def _update_xml(self, new_content: bytes):
		tmp_filename = f"{self._args.filename}.odsbutcher_{os.urandom(8).hex()}"
		with zipfile.ZipFile(self._args.filename, "r") as src, zipfile.ZipFile(tmp_filename, "w", zipfile.ZIP_DEFLATED) as dst:
			for info in src.infolist():
				if info.filename == self._xml_filename:
					dst.writestr(self._xml_filename, new_content)
				else:
					dst.writestr(info, src.read(info.filename))
		os.rename(tmp_filename, self._args.filename)

	def run(self):
		self._xml_filename = "styles.xml" if self.args.style_file else "content.xml"
		pretty_xml = self._read_xml()
		if self._args.edit_file:
			with tempfile.NamedTemporaryFile(suffix = ".xml", prefix = "odsbutcher_", mode = "w") as tmp:
				tmp.write(pretty_xml)
				tmp.flush()

				while True:
					subprocess.run([ os.environ["EDITOR"], tmp.name ], check = True)
					with open(tmp.name, "rb") as f:
						xmldoc = f.read()
					try:
						xml.dom.minidom.parseString(xmldoc)
					except xml.parsers.expat.ExpatError as e:
						print(f"Invalid XML: {e.__class__.__name__}")
						if self._confirm("Retry editing the XML document (y/n)? "):
							continue
						print("Document not saved.")
						return 1
					break
				self._update_xml(xmldoc)
		else:
			print(pretty_xml.rstrip("\r\n"))
