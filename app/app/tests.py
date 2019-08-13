from django.test import TestCase

from app.calc import add, subtract

class CalcTests(TestCase):

    def test_add_numbers(self):
        """ tests that two numbers are added together """
        self.assertEqual(add(0, 5), 5)

    def subtract_two_numbers(self):
        """ tests that two numbers are subtracted and returned """
        self.assertEqual(subtract(10, 20), 10)
