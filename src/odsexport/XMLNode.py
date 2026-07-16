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

import xml.dom.minidom

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

	def sort_attributes_recursively(self):
		if self._node.nodeType == self._node.ELEMENT_NODE:
			attributes = sorted(self._node.attributes.values(), key = lambda attr: ((attr.namespaceURI or ""), (attr.localName or attr.name)))
			for attr in attributes:
				self._node.removeAttributeNode(attr)
			for attr in attributes:
				self._node.setAttributeNode(attr)

		for child in self._node.childNodes:
			XMLNode(child).sort_attributes_recursively()

	@classmethod
	def normalize_namespaces(cls, document: xml.dom.minidom.Element, namespaces: dict[str, str]):
		assert(document.nodeType == document.DOCUMENT_NODE)
		def _normalize(node):
			if (node.nodeType == node.ELEMENT_NODE) and (node.namespaceURI in namespaces):
				prefix = namespaces[node.namespaceURI]
				document.renameNode(node, node.namespaceURI, f"{prefix}:{node.localName}")
			for child in list(node.childNodes):
				_normalize(child)
		_normalize(document)

	@classmethod
	def remove_text_whitespace(cls, node: xml.dom.minidom.Element):
		for child in list(node.childNodes):
			if child.nodeType == node.TEXT_NODE:
				text = child.data.strip()
				if text == "":
					node.removeChild(child)
					child.unlink()
				else:
					child.replaceWholeText(text)
			else:
				cls.remove_text_whitespace(child)

