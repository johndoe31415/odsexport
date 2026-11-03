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

import subprocess
import tempfile
from .MultiCommand import BaseAction
from .Tools import Tools

class ActionDiffXML(BaseAction):
	def run(self):
		xml_filename = self.args.custom_file if (self.args.custom_file is not None) else ("styles.xml" if self.args.style_file else "content.xml")
		xml1 = Tools.read_xml_from_ods(zip_filename = self.args.filename1, xml_filename = xml_filename, normalize_namespaces = not self._args.no_namespace_normalization, sort_attributes = not self._args.no_attribute_sort)
		xml2 = Tools.read_xml_from_ods(zip_filename = self.args.filename2, xml_filename = xml_filename, normalize_namespaces = not self._args.no_namespace_normalization, sort_attributes = not self._args.no_attribute_sort)
		with tempfile.NamedTemporaryFile(prefix = "odsbutcher_", suffix = ".xml", mode = "w") as f1, tempfile.NamedTemporaryFile(prefix = "odsbutcher_", suffix = ".xml", mode = "w") as f2:
			f1.write(xml1)
			f1.flush()
			f2.write(xml2)
			f2.flush()
			subprocess.run([ "diff", f1.name, f2.name ], check = False)
		return 0
