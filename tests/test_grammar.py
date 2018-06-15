import unittest
from grammar.grammar import Grammar
from grammar.production import Prod

class TestGrammar(unittest.TestCase):

    def test_remove_non_terminal(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', 'AB'),
            Prod('A', 'AB'),
            Prod('B', 'BB'),
            Prod('B', 'b')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        grammar.remove_non_terminal('B')

        result_prod = grammar.productions
        expected_prod = set()
        self.assertSetEqual(result_prod, expected_prod)

        result_non_terminal = grammar.non_terminals
        expected_non_terminal = set('SA')
        self.assertSetEqual(result_non_terminal, expected_non_terminal)

    def test_remove_terminal(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
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

        grammar.remove_terminal('a')

        result_prod = grammar.productions
        expected_prod = set([
            Prod('S', 'BC'),
            Prod('S', 'BD'),
            Prod('A', 'cC'),
            Prod('A', 'AB'),
            Prod('B', 'bB'),
            Prod('B', Grammar.EPSILON),
            Prod('C', 'BC'),
            Prod('D', 'dDd'),
            Prod('D', 'c')
        ])
        self.assertSetEqual(result_prod, expected_prod)

        result_terminal = grammar.terminals
        expected_terminal = set('bcd')
        self.assertSetEqual(result_terminal, expected_terminal)

    def test_productive(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
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

    def test_is_empty_false(self):
        '''
        Test example got from here:
        https://www.eecs.yorku.ca/course_archive/2001-02/S/2001B/lectures/l.pdf
        '''
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', 'AB'),
            Prod('A', 'BB'),
            Prod('A', 'a'),
            Prod('B', 'AB'),
            Prod('B', 'b')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_empty()

        self.assertFalse(result)

    def test_is_empty_true(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', 'AB'),
            Prod('A', 'AB'),
            Prod('B', 'BB'),
            Prod('B', 'b')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_empty()

        self.assertTrue(result)
