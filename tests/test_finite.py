import unittest

from grammar import Grammar, Prod

class TestFinite(unittest.TestCase):

    def test_is_finite_true(self):
        non_terminals = set('SA')
        terminals = set('ab')
        productions = set([
            Prod('S', ('a',)),
            Prod('S', ('A',)),
            Prod('A', ('b',)),
            Prod('A', ('S',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_finite()

        self.assertTrue(result)

    def test_is_finite_false(self):
        non_terminals = set('S')
        terminals = set('a')
        productions = set([
            Prod('S', ('a', 'S')),
            Prod('S', ('a',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_finite()

        self.assertFalse(result)

    def test_is_finite(self):
        non_terminals = set('ETF')
        terminals = set('+*()') | { 'id' }
        productions = {
            Prod('E', ('E', '+', 'T')),
            Prod('E', ('T',)),
            Prod('T', ('T', '*', 'F')),
            Prod('T', ('F',)),
            Prod('F', ('(', 'E', ')')),
            Prod('F', ('id',))
        }
        start = 'E'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_finite()

        self.assertFalse(result)
