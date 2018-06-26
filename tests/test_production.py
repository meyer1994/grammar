import unittest

from grammar import Prod

class TestProduction(unittest.TestCase):

    def test_constructor(self):
        p = Prod('A', 'b')
        self.assertEqual(p.n, 'A')
        self.assertEqual(p.p, 'b')
