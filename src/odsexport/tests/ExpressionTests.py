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

import unittest
from odsexport.Formula import Expression, Constant, BinaryOperation, CellRef, FunctionArgument, Function


class ExpressionTests(unittest.TestCase):
	def test_simple_add(self):
		expr = BinaryOperation(BinaryOperation(1, "+", 2), "+", 3)
		self.assertEqual(expr.render(), "1+2+3")

		expr = BinaryOperation(1, "+", BinaryOperation(2, "+", 3))
		self.assertEqual(expr.render(), "1+2+3")

	def test_simple_sub(self):
		expr = BinaryOperation(BinaryOperation(1, "-", 2), "-", 3)
		self.assertEqual(expr.render(), "1-2-3")

		expr = BinaryOperation(1, "-", BinaryOperation(2, "-", 3))
		self.assertEqual(expr.render(), "1-(2-3)")

	def test_simple_mul(self):
		expr = BinaryOperation(BinaryOperation(1, "*", 2), "*", 3)
		self.assertEqual(expr.render(), "1*2*3")

		expr = BinaryOperation(1, "*", BinaryOperation(2, "*", 3))
		self.assertEqual(expr.render(), "1*2*3")

	def test_simple_div(self):
		expr = BinaryOperation(BinaryOperation(1, "/", 2), "/", 3)
		self.assertEqual(expr.render(), "1/2/3")

		expr = BinaryOperation(1, "/", BinaryOperation(2, "/", 3))
		self.assertEqual(expr.render(), "1/(2/3)")

	def test_simple_mul_before_add(self):
		expr = Constant(1) + Constant(2) * Constant(3)
		self.assertEqual(expr.render(), "1+2*3")

		expr = (Constant(1) + Constant(2)) * Constant(3)
		self.assertEqual(expr.render(), "(1+2)*3")

	def test_function(self):
		expr = Function("FOO", 1, 2, "blah \" muh")
		self.assertEqual(expr.render(), "FOO(1;2;\"blah \"\" muh\")")

	def test_comparison(self):
		expr = Constant(10) > 20
		self.assertEqual(expr.render(), "10>20")

	def test_comparison_and_or(self):
		expr = ((Constant(10) > 20) & (Constant(30) > 40)) | (Constant(50) >= 60)
		self.assertEqual(expr.render(), "OR(AND(10>20;30>40);50>=60)")

	def test_not(self):
		expr = ~(Constant(10) > 20)
		self.assertEqual(expr.render(), "NOT(10>20)")

	def test_neg(self):
		expr = -(Constant(1) - (Constant(2) - 3))
		self.assertEqual(expr.render(), "-(1-(2-3))")

	def test_neg(self):
		# Jesus Christ this is fully legal Excel for you
		expr = -(Constant(1) - (-2))
		self.assertEqual(expr.render(), "-(1--2)")

		expr = Constant(1) - (-2)
		self.assertEqual(expr.render(), "1--2")
