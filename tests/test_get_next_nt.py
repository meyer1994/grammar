import unittest

from grammar import Grammar, Prod

class TestGetNextNT(unittest.TestCase):
    def setUp(self):
        non_terminals = { 'S', 'A0', 'A1', 'A2', 'B67', 'B150', 'B1000' }
        terminals = set('abcde')
        productions = set([
            Prod('S', ('a','S')),
            Prod('S', ('A','b')),
            Prod('A0', ('A','b')),
            Prod('A1', ('B','c')),
            Prod('A2', ('a',)),
            Prod('B67', ('B','d')),
            Prod('B150', ('S','a')),
            Prod('B1000', ('e',))
        ])
        start = 'S'
        self.grammar = Grammar(non_terminals, terminals, productions, start)

    def test_get_next(self):
        tests = [
            'A',
            'B'
        ]
        expected = [
            'A3',
            'B0'
        ]

        for test, exp in zip(tests, expected):
            res = self.grammar._get_next_nt(test)
            print(test, res)
            self.assertEqual(res, exp)
