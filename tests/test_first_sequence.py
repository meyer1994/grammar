import unittest

from grammar import Grammar, Prod

class TestFirstSequence(unittest.TestCase):
    def setUp(self):
        non_terminals = set('SABC')
        terminals = set('abcd')
        productions = {
            Prod('S', ('B', 'C')),
            Prod('S', ('A', 'B')),
            Prod('A', ('a', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
            Prod('B', ('d',)),
            Prod('C', ('c', 'C')),
            Prod('C', ('c',))
        }
        start = 'S'
        self.grammar = Grammar(non_terminals, terminals, productions, start)

    def test_sequence(self):
        tests = [
            ('B', 'C'),
            ('A', 'B'),
            ('a', 'A'),
            (Grammar.EPSILON,),
            ('b', 'B'),
            ('d',),
            ('c', 'C'),
            ('c',)
        ]
        expected = [
            { 'd', 'b' },
            { 'a', 'd', 'b' },
            { 'a' },
            { Grammar.EPSILON },
            { 'b' },
            { 'd' },
            { 'c' },
            { 'c' }
        ]

        first = self.grammar.first_sets()
        non_term = self.grammar.non_terminals
        for test, exp in zip(tests, expected):
            res = self.grammar._first_sequence(first, test) - non_term
            self.assertSetEqual(res, exp)
