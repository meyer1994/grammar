import unittest

from grammar import Grammar, Prod

class TestSimple(unittest.TestCase):

    def test_remove_simple(self):
        non_terminals = set('SFGH')
        terminals = set('abcd')
        productions = {
            Prod('S', ('F', 'G', 'H')),
            Prod('F', ('G',)),
            Prod('F', ('a',)),
            Prod('G', ('d', 'G')),
            Prod('G', ('H',)),
            Prod('G', ('b',)),
            Prod('H', ('c',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_simple()

        exp_non_terminals = set('SFGH')
        exp_terminals = grammar.terminals.copy()
        exp_productions = {
            Prod('S', ('F', 'G', 'H')),
            Prod('F', ('a',)),
            Prod('F', ('d', 'G')),
            Prod('F', ('b',)),
            Prod('F', ('c',)),
            Prod('G', ('d', 'G')),
            Prod('G', ('b',)),
            Prod('G', ('c',)),
            Prod('H', ('c',))
        }
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        self.assertEqual(grammar, exp_grammar)

    def test_recursion(self):
        non_terminals = set('S')
        terminals = set('a')
        productions = {
            Prod('S', ('a', 'S')),
            Prod('S', ('S',)),
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        exp_non_terminals = set('S')
        exp_terminals = set(grammar.terminals)
        exp_productions = {
            Prod('S', ('a', 'S')),
        }
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        grammar.remove_simple()

        self.assertEqual(grammar, exp_grammar)
