import unittest
from grammar.grammar import Grammar
from grammar.production import Prod

class TestGrammar(unittest.TestCase):

    def test_remove_non_terminal(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('A', 'B')),
            Prod('A', ('A', 'B')),
            Prod('B', ('B', 'B')),
            Prod('B', ('b',))
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
            Prod('S', ('a', 'S')),
            Prod('S', ('B', 'C')),
            Prod('S', ('B', 'D')),
            Prod('A', ('c', 'C')),
            Prod('A', ('A', 'B')),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,)),
            Prod('C', ('a', 'A')),
            Prod('C', ('B', 'C')),
            Prod('D', ('d', 'D', 'd')),
            Prod('D', ('c',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        grammar.remove_terminal('a')

        result_prod = grammar.productions
        expected_prod = set([
            Prod('S', ('B', 'C')),
            Prod('S', ('B', 'D')),
            Prod('A', ('c', 'C')),
            Prod('A', ('A', 'B')),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,)),
            Prod('C', ('B', 'C')),
            Prod('D', ('d', 'D', 'd')),
            Prod('D', ('c',))
        ])
        self.assertSetEqual(result_prod, expected_prod)

        result_terminal = grammar.terminals
        expected_terminal = set('bcd')
        self.assertSetEqual(result_terminal, expected_terminal)

    def test_remove_unproductive(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
        productions = set([
            Prod('S', ('a', 'S')),
            Prod('S', ('B', 'C')),
            Prod('S', ('B', 'D')),
            Prod('A', ('c', 'C')),
            Prod('A', ('A', 'B')),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,)),
            Prod('C', ('a', 'A')),
            Prod('C', ('B', 'C')),
            Prod('D', ('d', 'D', 'd')),
            Prod('D', ('c',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        grammar.remove_unproductive()

        exp_non_terminals = set('SBD')
        exp_terminals = set(grammar.terminals)
        exp_productions = set([
            Prod('S', ('a', 'S')),
            Prod('S', ('B', 'D')),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,)),
            Prod('D', ('d', 'D', 'd')),
            Prod('D', ('c',))
        ])
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        self.assertEqual(grammar, exp_grammar)

    def test_remove_unreachable(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
        productions = set([
            Prod('S', ('a', 'S', 'a')),
            Prod('S', ('d', 'D', 'd')),
            Prod('A', ('a', 'B')),
            Prod('A', ('C', 'c')),
            Prod('A', ('a',)),
            Prod('B', ('d', 'D')),
            Prod('B', ('b', 'B')),
            Prod('B', ('b',)),
            Prod('C', ('A', 'a')),
            Prod('C', ('d', 'D')),
            Prod('C', ('c',)),
            Prod('D', ('b', 'b', 'B')),
            Prod('D', ('d',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        result = grammar.remove_unreachable()

        exp_non_terminals = set('SDB')
        exp_terminals = set('abd')
        exp_productions = set([
            Prod('S', ('a', 'S', 'a')),
            Prod('S', ('d', 'D', 'd')),
            Prod('B', ('d', 'D')),
            Prod('B', ('b', 'B')),
            Prod('B', ('b',)),
            Prod('D', ('b', 'b', 'B')),
            Prod('D', ('d',))
        ])
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        self.assertEqual(grammar, exp_grammar)

    def test_remove_useless(self):
        non_terminals = set('SABCDEF')
        terminals = set('abcdef')
        productions = set([
            Prod('S', ('a', 'S', 'a')),
            Prod('S', ('F', 'b', 'D')),
            Prod('S', ('B', 'E')),
            Prod('A', ('a', 'A')),
            Prod('A', ('C', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
            Prod('B', ('F', 'E')),
            Prod('C', ('c', 'C', 'b')),
            Prod('C', ('A', 'c', 'A')),
            Prod('D', ('D', 'd')),
            Prod('D', ('f', 'F')),
            Prod('D', ('c',)),
            Prod('E', ('B', 'C')),
            Prod('E', ('e', 'E')),
            Prod('E', ('E', 'B')),
            Prod('F', ('f', 'F')),
            Prod('F', ('D', 'd'))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        result = grammar.remove_useless()

        exp_non_terminals = set('SFD')
        exp_terminals = set('abcdf')
        exp_productions = set([
            Prod('S', ('a', 'S', 'a')),
            Prod('S', ('F', 'b', 'D')),
            Prod('F', ('D', 'd')),
            Prod('F', ('f', 'F')),
            Prod('D', ('c',)),
            Prod('D', ('f', 'F')),
            Prod('D', ('D', 'd'))
        ])
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        print(grammar.terminals)
        print(exp_grammar.terminals)

        self.assertEqual(grammar, exp_grammar)

    def test_remove_epsilon1(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
        productions = set([
            Prod('S', ('A', 'b', 'B')),
            Prod('S', ('A', 'D')),
            Prod('A', ('a', 'A')),
            Prod('A', ('B',)),
            Prod('B', ('S', 'B', 'D')),
            Prod('B', ('C', 'D')),
            Prod('C', ('c', 'C')),
            Prod('C', ('A', 'S')),
            Prod('C', (Grammar.EPSILON,)),
            Prod('D', ('d', 'D')),
            Prod('D', (Grammar.EPSILON,))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_epsilon()


        exp_non_terminals = set([ "S'", 'S', 'A', 'B', 'C', 'D' ])
        exp_terminals = set('abcd')
        exp_productions = set([
            Prod("S'", (Grammar.EPSILON,)),
            Prod("S'", ('S',)),
            Prod('S', ('b',)),
            Prod('S', ('D',)),
            Prod('S', ('A',)),
            Prod('S', ('b', 'B')),
            Prod('S', ('A', 'b')),
            Prod('S', ('A', 'b', 'B')),
            Prod('S', ('A', 'D')),
            Prod('A', ('a',)),
            Prod('A', ('a', 'A')),
            Prod('A', ('B',)),
            Prod('B', ('S', 'B')),
            Prod('B', ('S',)),
            Prod('B', ('S', 'D')),
            Prod('B', ('B',)),
            Prod('B', ('C',)),
            Prod('B', ('C', 'D')),
            Prod('B', ('D',)),
            Prod('B', ('S', 'B', 'D')),
            Prod('B', ('B', 'D')),
            Prod('C', ('A',)),
            Prod('C', ('S',)),
            Prod('C', ('c', 'C')),
            Prod('C', ('A', 'S')),
            Prod('C', ('c',)),
            Prod('D', ('d', 'D')),
            Prod('D', ('d',))
        ])
        exp_start = "S'"
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        print(grammar)
        print('================')
        print(exp_grammar)

        self.assertEqual(grammar, exp_grammar)

    def test_remove_epsilon2(self):
        non_terminals = set('SA')
        terminals = set('a')
        productions = set([
            Prod('S', ('a', 'A')),
            Prod('A', ('a', 'A')),
            Prod('A', ('a',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_epsilon()


        exp_non_terminals = set('SA')
        exp_terminals = set('a')
        exp_productions = set([
            Prod('S', ('a', 'A')),
            Prod('A', ('a', 'A')),
            Prod('A', ('a',))
        ])
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        self.assertEqual(grammar, exp_grammar)

    def test_productive(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
        productions = set([
            Prod('S', ('a', 'S')),
            Prod('S', ('B', 'C')),
            Prod('S', ('B', 'D')),
            Prod('A', ('c', 'C')),
            Prod('A', ('A', 'B')),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,)),
            Prod('C', ('a', 'A')),
            Prod('C', ('B', 'C')),
            Prod('D', ('d', 'D', 'd')),
            Prod('D', ('c',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.productive()
        expected = set('BDS')

        self.assertSetEqual(result, expected)

    def test_reachable(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
        productions = set([
            Prod('S', ('a', 'S', 'a')),
            Prod('S', ('d', 'D', 'd')),
            Prod('A', ('a', 'B')),
            Prod('A', ('C', 'c')),
            Prod('A', ('a',)),
            Prod('B', ('d', 'D')),
            Prod('B', ('b', 'B')),
            Prod('B', ('b',)),
            Prod('C', ('A', 'a')),
            Prod('C', ('d', 'D')),
            Prod('C', ('c',)),
            Prod('D', ('b', 'b', 'B')),
            Prod('D', ('d',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.reachable()
        expected = set('SBDabd')

        self.assertSetEqual(result, expected)

    def test_is_empty_false(self):
        '''
        Test example got from here:
        https://www.eecs.yorku.ca/course_archive/2001-02/S/2001B/lectures/l.pdf
        '''
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('A', 'B')),
            Prod('A', ('B', 'B')),
            Prod('A', ('a',)),
            Prod('B', ('A', 'B')),
            Prod('B', ('b',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_empty()

        self.assertFalse(result)

    def test_is_empty_true(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('A', 'B')),
            Prod('A', ('A', 'B')),
            Prod('B', ('B', 'B')),
            Prod('B', ('b',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.is_empty()

        self.assertTrue(result)

    def test_equal_true(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('A', 'B')),
            Prod('A', ('A', 'B')),
            Prod('B', ('B', 'B')),
            Prod('B', ('b',))
        ])
        start = 'S'
        grammar0 = Grammar(non_terminals, terminals, productions, start)
        grammar1 = Grammar(non_terminals, terminals, productions, start)

        self.assertTrue(grammar0 == grammar1)

    def test_equal_false(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('A', 'B')),
            Prod('A', ('A', 'B')),
            Prod('B', ('B', 'B')),
            Prod('B', ('b',))
        ])
        start = 'S'
        grammar0 = Grammar(non_terminals, terminals, productions, start)

        # Remove random item
        prods1 = productions.copy()
        prods1.pop()
        grammar1 = Grammar(non_terminals, terminals, prods1, start)

        self.assertFalse(grammar0 == grammar1)

    def test_closure(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('A', 'B')),
            Prod('A', ('a', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar._closure()
        expected = set([ (i,) for i in 'SAB' ])

        self.assertSetEqual(result, expected)

    def test_get_productions_by_non_terminal(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('A', 'B')),
            Prod('A', ('a', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        exp_results = [
            ('S', [ ('A', 'B') ]),
            ('A', [ ('a', 'A'), (Grammar.EPSILON,) ]),
            ('B', [ ('b', 'B'), (Grammar.EPSILON,) ])
        ]

        for n, p in exp_results:
            res = grammar._get_productions_by_non_terminal(n)
            res.sort()
            p.sort()
            self.assertListEqual(res, p)

    def test_str(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = set([
            Prod('S', ('AB',)),
            Prod('A', ('aA',)),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('bB',)),
            Prod('B', (Grammar.EPSILON,))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        lines = set(str(grammar))
        exp_lines = set(
            f'''S -> AB
            A -> aA | {Grammar.EPSILON}
            B -> bB | {Grammar.EPSILON}'''
        )

        self.assertSetEqual(lines, exp_lines)
