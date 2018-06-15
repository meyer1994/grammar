import unittest
from grammar.grammar import Grammar
from grammar.production import Prod

class TestGrammar(unittest.TestCase):

    def test_productive(self):
        non_terminals = set(list('SABCD'))
        terminals = set(list('abcd'))
        productions = set([
            Prod('S', 'aS'),
            Prod('S', 'BC'),
            Prod('S', 'BD'),
            Prod('A', 'cC'),
            Prod('A', 'AB'),
            Prod('B', 'bB'),
            Prod('B', Grammar.EPSILON),
            Prod('C', 'aA'),
            Prod('C', 'BC'),
            Prod('D', 'dDd'),
            Prod('D', 'c')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.productive()
        expected = set(list('BDS'))

        self.assertSetEqual(result, expected)
