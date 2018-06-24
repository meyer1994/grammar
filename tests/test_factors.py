import unittest

from pprint import pprint

from grammar.grammar import Grammar
from grammar.production import Prod

class TestFactors(unittest.TestCase):
    def setUp(self):
        non_terminals = set('SB')
        terminals = set('abd')
        productions = set([
            Prod('S', ('a','S')),
            Prod('S', ('a','B')),
            Prod('S', ('d','S')),
            Prod('B', ('b','B')),
            Prod('B', ('b',))
        ])
        start = 'S'
        self.grammar = Grammar(non_terminals, terminals, productions, start)

    def test_is_factored_true(self):
        non_terminals = set([ 'S', 'S0', 'B', 'B0' ])
        terminals = set('abd')
        productions = set([
            Prod('S', ('a','S0')),
            Prod('S', ('d','S')),
            Prod('S0', ('B',)),
            Prod('S0', ('S',)),
            Prod('B', ('b','B0')),
            Prod('B0', ('B',)),
            Prod('B0', (Grammar.EPSILON,)),
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_factored()
        self.assertTrue(result)

    def test_is_factored_false(self):
        result = self.grammar.is_factored()
        self.assertFalse(result)

    def test_get_factors(self):
        tests = [
            'S',
            'B'
        ]
        expected = [
            [{ ('a', 'S'), ('a', 'B') }, { ('d', 'S') }],
            [{ ('b',), ('b', 'B') }]
        ]

        for test, exp in zip(tests, expected):
            res = self.grammar._get_factors(test)
            frozen_res = set(map(lambda s: frozenset(s), res))
            frozen_exp = set(map(lambda s: frozenset(s), exp))
            self.assertSetEqual(frozen_res, frozen_exp)

    def test_factor(self):
        exp_non_terminals = { 'S', 'S0', 'B' }
        exp_terminals = set('abd')
        exp_productions = {
            Prod('S', ('a', 'S0')),
            Prod('S', ('d', 'S')),
            Prod('S0', ('B',)),
            Prod('S0', ('S',)),
            Prod('B', ('b', 'B')),
            Prod('B', ('b',))
        }
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        factors = { ('a','S'), ('a','B') }
        self.grammar._factor('S', factors)
        self.assertEqual(self.grammar, exp_grammar)

        exp_productions = {
            Prod('S', ('a', 'S0')),
            Prod('S', ('d', 'S')),
            Prod('S0', ('B',)),
            Prod('S0', ('S',)),
            Prod('B', ('b', 'B0')),
            Prod('B0', ('B',)),
            Prod('B0', (Grammar.EPSILON,))
        }
        exp_non_terminals |= { 'B0' }
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)


        factors = { ('b', 'B'), ('b',) }
        self.grammar._factor('B', factors)
        self.assertEqual(self.grammar, exp_grammar)

    def test_factor_part(self):
        tests = [
            { ('a', 'S'), ('a', 'B') },
            { ('b', 'B'), ('b',) }
        ]
        expected = [
            [ 'a' ],
            [ 'b' ]
        ]

        for test, exp in zip(tests, expected):
            res = self.grammar._get_factor_part(test)
            self.assertListEqual(res, exp)

    def test_factor_steps(self):
        res = self.grammar.factor()
        self.assertFalse(res)

        non_terminals = { 'S', 'S0', 'B', 'B0' }
        terminals = set('abd')
        productions = {
            Prod('S', ('a','S0')),
            Prod('S', ('d','S')),
            Prod('S0', ('B',)),
            Prod('S0', ('S',)),
            Prod('B', ('b','B0')),
            Prod('B0', ('B',)),
            Prod('B0', (Grammar.EPSILON,)),
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        res = self.grammar.factor(2)
        self.assertEqual(grammar, res)

        res = self.grammar.factor(10)
        self.assertEqual(grammar, res)

    def test_factor_loop(self):
        non_terminals = set('AS')
        terminals = set('ac')
        productions = {
            Prod('S', ('a','S')),
            Prod('S', ('A',)),
            Prod('A', ('a', 'A', 'c')),
            Prod('A', (Grammar.EPSILON,))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.factor(10)
        self.assertFalse(result)
