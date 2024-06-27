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

class XMLNode():
	def __init__(self, node):
		self._node = node

	def set_ns_attributes(self, namespace: str, attributes: dict[str, str]):
		for (key, value) in attributes.items():
			self._node.setAttributeNS(namespace, f"{namespace}:{key}", value)

	def get_child_with_tag(self, tag: str):
		for child in self._node.childNodes:
			if (child.nodeType == self._node.ELEMENT_NODE) and (child.tagName == tag):
				yield child

	def get_first_child_with_tag(self, tag: str):
		return next(self.get_child_with_tag(tag))
