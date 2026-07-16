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

import sys
from . import FriendlyArgumentParser, MultiCommand
from .ActionDumpXML import ActionDumpXML

def main():
	mc = MultiCommand(description = "Perform debugging actions on ODS files")
	def genparser(parser):
		parser.add_argument("--no-attribute-sort", action = "store_true", help = "Do not sort attributes lexicographically before printing XML.")
		parser.add_argument("--no-namespace-normalization", action = "store_true", help = "Do not normalize XML namespaces before printing XML.")
		parser.add_argument("-e", "--edit-file", action = "store_true", help = "Edit the XML file instead of just printing it to stdout.")
		parser.add_argument("-s", "--style-file", action = "store_true", help = "Print style.xml instead of content.xml")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
		parser.add_argument("filename", help = "ODS file to dump content from")
	mc.register("dumpxml", "Dump (or edit) the XML of an ODS file", genparser, action = ActionDumpXML)

	returncode = mc.run(sys.argv[1:])
	return (returncode or 0)

if __name__ == "__main__":
	import sys
	main(sys.argv[1:])
