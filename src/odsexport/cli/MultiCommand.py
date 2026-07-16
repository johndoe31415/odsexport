#!/usr/bin/python3
#
#	MultiCommand - Provide an openssl-style multi-command abstraction
#	Copyright (C) 2011-2026 Johannes Bauer
#
#	This file is part of pycommon.
#
#	pycommon is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pycommon is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pycommon; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#
#	File UUID 4c6b89d0-ec0c-4b19-80d1-4daba7d80967

import sys
import collections
import textwrap
import logging
from .FriendlyArgumentParser import FriendlyArgumentParser
from .PrefixMatcher import PrefixMatcher

class MultiCommand():
	RegisteredCommand = collections.namedtuple("RegisteredCommand", [ "name", "description", "parser", "action", "aliases", "visible" ])
	ParseResult = collections.namedtuple("ParseResults", [ "cmd", "args" ])

	def __init__(self, description = None, trailing_text = None):
		self._description = description
		self._trailing_text = trailing_text
		self._commands = collections.OrderedDict()
		self._aliases = { }

	def _create_command_parser(self, parser_generator: callable, commandname: str, description: str):
		parser = FriendlyArgumentParser(prog = f"{sys.argv[0]} {commandname}", description = description, add_help = False)
		parser_generator(parser)
		parser.add_argument("--help", action = "help", help = "Show this help page.")
		return parser

	def register(self, commandname: str, description: str, parser_generator: callable, **kwargs):
		supported_kwargs = set(("aliases", "action", "visible"))
		if len(set(kwargs.keys()) - supported_kwargs) > 0:
			raise ValueError(f"Unsupported kwarg found. Supported: {', '.join(sorted(list(supported_kwargs)))}")

		if (commandname in self._commands) or (commandname in self._aliases):
			raise Exception(f"Command '{commandname}' already registered.")

		aliases = kwargs.get("aliases", [ ])
		action = kwargs.get("action")
		for alias in aliases:
			if (alias in self._commands) or (alias in self._aliases):
				raise Exception(f"Alias '{alias}' already registered.")
			self._aliases[alias] = commandname

		parser = self._create_command_parser(parser_generator, commandname, description)
		cmd = self.RegisteredCommand(name = commandname, description = description, parser = parser, action = action, aliases = aliases, visible = kwargs.get("visible", True))
		self._commands[commandname] = cmd

	def _show_syntax(self, msg: str | None = None):
		output_file = sys.stderr if (msg is not None) else sys.stdout
		if msg is not None:
			print(f"Error: {msg}", file = output_file)
		print(f"usage: {sys.argv[0]} [command] [options]", file = output_file)
		print(file = output_file)
		if self._description is not None:
			print(self._description, file = output_file)
			print(file = output_file)
		print("Available commands:", file = output_file)
		for (commandname, command) in self._commands.items():
			if not command.visible:
				continue
			commandname_line = command.name
			for description_line in textwrap.wrap(command.description, width = 56):
				print("    %-15s    %s" % (commandname_line, description_line), file = output_file)
				commandname_line = ""
		print(file = output_file)
		if self._trailing_text is not None:
			for line in textwrap.wrap(self._trailing_text, width = 80):
				print(line, file = output_file)
			print(file = output_file)
		print("Options vary from command to command. To receive further info, type", file = output_file)
		print("    %s [command] --help" % (sys.argv[0]), file = output_file)

	def _show_syntax_cmd(self, cmdname: str, *args):
		self._show_syntax()
		return 0

	def _raise_error(self, msg: str, silent: bool = False):
		if silent:
			raise Exception(msg)
		else:
			self._show_syntax(msg)
			sys.exit(1)

	def _getcmdnames(self) -> set[str]:
		return set(self._commands.keys()) | set(self._aliases.keys())

	def parse(self, cmdline: list[str], silent: bool = False) -> ParseResult:
		if len(cmdline) < 1:
			self._raise_error("No command supplied.")

		# Check if we can match the command portion
		pm = PrefixMatcher(self._getcmdnames() | set([ "-h", "--help" ]))
		try:
			supplied_cmd = pm.matchunique(cmdline[0])
		except Exception as e:
			self._raise_error(f"Invalid command supplied: {str(e)}")

		if supplied_cmd in [ "-h", "--help" ]:
			return self.ParseResult(cmd = self.RegisteredCommand(name = "--help", description = None, parser = None, action = self._show_syntax_cmd, aliases = None, visible = False), args = None)
		elif supplied_cmd in self._aliases:
			supplied_cmd = self._aliases[supplied_cmd]

		command = self._commands[supplied_cmd]
		command.parser.setsilenterror(silent)
		args = command.parser.parse_args(cmdline[1:])
		return self.ParseResult(command, args)

	def run(self, cmdline: list[str], silent: bool = False):
		parseresult = self.parse(cmdline, silent)
		if parseresult.cmd.action is None:
			raise Exception(f"Should run command '{parseresult.cmd.name}', but no action was registered.")
		result = parseresult.cmd.action(self, parseresult.cmd.name, parseresult.args)
		if hasattr(result, "run"):
			result = result.run()
		return result

class BaseAction():
	def __init__(self, multi_command: MultiCommand, cmd: str, args):
		self._multi_command = multi_command
		self._cmd = cmd
		self._args = args

	def _run_command(self, cmdline: list[str]):
		return self._multi_command.run(cmdline = cmdline)

	@property
	def cmd(self):
		return self._cmd

	@property
	def args(self):
		return self._args

	def run(self):
		raise NotImplementedError(self.__class__.__name__)

class LoggingAction(BaseAction):
	def __init__(self, multi_command: MultiCommand, cmd: str, args):
		super().__init__(multi_command, cmd, args)
		if self.args.verbose == 0:
			loglevel = logging.WARNING
		elif self.args.verbose == 1:
			loglevel = logging.INFO
		else:
			loglevel = logging.DEBUG
		logging.basicConfig(format = "{name:>20s} [{levelname:.1s}]: {message}", style = "{", level = loglevel)

if __name__ == "__main__":
	class ImportAction(BaseAction):
		def run(self):
			print("Import:", self.cmd, self.args)
			return self.args.returncode

	class ExportAction(BaseAction):
		def run(self):
			print("Export:", self.cmd, self.args)

	mc = MultiCommand(description = "Run multiple export- and importthings")
	def genparser(parser):
		parser.add_argument("-r", "--returncode", metavar = "value", type = int, required = True, help = "Gives the exit code. Mandatory argument.")
		parser.add_argument("-i", "--infile", metavar = "filename", required = True, help = "Specifies the input text file that is to be imported. Mandatory argument.")
		parser.add_argument("-n", "--world", metavar = "name", choices = [ "world", "foo", "bar" ], default = "overworld", help = "Specifies the world name. Possible options are %(choices)s. Default is %(default)s.")
		parser.add_argument("-h", "--hello", action = "store_true", help = "Print 'hello world'")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
	mc.register("import", "Import some file from somewhere", genparser, action = ImportAction, aliases = [ "ymport" ])

	def genparser(parser):
		parser.add_argument("-o", "--outfile", metavar = "filename", help = "Specifies the input text file that is to be imported.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be given multiple times.")
	mc.register("export", "Export some file to somewhere", genparser, action = ExportAction)

	returncode = mc.run(sys.argv[1:])
	sys.exit(returncode or 0)
