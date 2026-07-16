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

Namespaces = {
	"styles.xml": {
		"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
		"number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
		"style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
		"fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
	},
	"manifest.xml": {
		"manifest": "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
	},
	"content.xml": {
		"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
		"chart": "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
		"css3t": "http://www.w3.org/TR/css3-text/",
		"dc": "http://purl.org/dc/elements/1.1/",
		"dom": "http://www.w3.org/2001/xml-events",
		"dr3d": "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
		"draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
		"drawooo": "http://openoffice.org/2010/draw",
		"field": "urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0",
		"fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
		"form": "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
		"formx": "urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0",
		"grddl": "http://www.w3.org/2003/g/data-view#",
		"math": "http://www.w3.org/1998/Math/MathML",
		"meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
		"number": "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
		"of": "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
		"ooo": "http://openoffice.org/2004/office",
		"oooc": "http://openoffice.org/2004/calc",
		"ooow": "http://openoffice.org/2004/writer",
		"presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
		"rpt": "http://openoffice.org/2005/report",
		"script": "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
		"style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
		"svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
		"table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
		"tableooo": "http://openoffice.org/2009/table",
		"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
		"xforms": "http://www.w3.org/2002/xforms",
		"xhtml": "http://www.w3.org/1999/xhtml",
		"xlink": "http://www.w3.org/1999/xlink",
		"xsd": "http://www.w3.org/2001/XMLSchema",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance",
	},
	"meta.xml": {
		"grddl": "http://www.w3.org/2003/g/data-view#",
		"meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
		"dc": "http://purl.org/dc/elements/1.1/",
		"xlink": "http://www.w3.org/1999/xlink",
		"ooo": "http://openoffice.org/2004/office",
		"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
	}
}
