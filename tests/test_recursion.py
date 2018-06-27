import unittest

from copy import deepcopy

from grammar import Grammar, Prod

class TestRecursion(unittest.TestCase):

    def test_proper_recursion(self):
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

        result = grammar.has_indirect_left_recursion()
        self.assertFalse(result)

    def test_has_indirect_left_recursion_true(self):
        non_terminals = set('SA')
        terminals = set('abcd')
        productions = {
            Prod('S', ('A','a')),
            Prod('S', ('S','b')),
            Prod('A', ('S','c')),
            Prod('A', ('d',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.has_indirect_left_recursion()
        self.assertTrue(result)

    def test_has_indirect_left_recursion_true2(self):
        non_terminals = set('SAB')
        terminals = set('abcde')
        productions = {
            Prod('S', ('a','S')),
            Prod('S', ('A','b')),
            Prod('A', ('A','b')),
            Prod('A', ('B','c')),
            Prod('A', ('a',)),
            Prod('B', ('B','d')),
            Prod('B', ('S','a')),
            Prod('B', ('e',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.has_indirect_left_recursion()
        self.assertTrue(result)

    def test_has_indirect_left_recursion_true3(self):
        non_terminals = set('SABCD')
        terminals = set('abcd')
        productions = {
            Prod('S', ('a', 'S')),
            Prod('S', ('B', 'C')),
            Prod('S', ('B', 'D')),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,)),
            Prod('A', ('A', 'B')),
            Prod('A', ('c', 'C')),
            Prod('C', ('a', 'A')),
            Prod('C', ('B', 'C')),
            Prod('D', ('d', 'D', 'd')),
            Prod('D', ('c',))
        }
        start = 'S'

        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.has_indirect_left_recursion()
        self.assertTrue(result)

    def test_has_indirect_left_recursion_false(self):
        non_terminals = { 'S' }
        terminals = set('ab')
        productions = {
            Prod('S', ('S','a')),
            Prod('S', ('b',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.has_indirect_left_recursion()
        self.assertFalse(result)

    def test_has_indirect_left_recursion_false2(self):
        non_terminals = set('ETF')
        terminals = set('+*()') | { 'id' }
        productions = {
            Prod('E', ('E','+','T')),
            Prod('E', ('T',)),
            Prod('T', ('T','*','F')),
            Prod('T', ('F',)),
            Prod('F', ('(','E',')')),
            Prod('F', ('id',))
        }
        start = 'E'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.has_indirect_left_recursion()
        self.assertFalse(result)

    def test_has_direct_left(self):
        non_terminals = { 'S' }
        terminals = set('ab')
        productions = {
            Prod('S', ('S','a')),
            Prod('S', ('b',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar.has_direct_left_recursion()
        self.assertTrue(result)

    def test_has_left_recursion_true(self):
        non_terminals = { 'S' }
        terminals = set('ab')
        productions = {
            Prod('S', ('S','a')),
            Prod('S', ('b',))
        }
        start = 'S'

        grammar = Grammar(non_terminals, terminals, productions, start)
        result = grammar.has_left_recursion()
        self.assertTrue(result)

    def test_has_left_recursion_false(self):
        non_terminals = set(['S', 'S1', 'A'])
        terminals = set('abcd')
        productions = set([
            Prod('S1', ('c','a','S1')),
            Prod('S1', ('b','S1')),
            Prod('S1', (Grammar.EPSILON,)),
            Prod('S', ('d','a','S1')),
            Prod('A', ('S','c')),
            Prod('A', ('d',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        self.assertFalse(grammar.has_left_recursion())


    def test_epslon_remove_recursion(self):
        non_terminals = set('SAB')
        terminals = set('ab')
        productions = {
            Prod('S', ('A', 'B')),
            Prod('A', ('a', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        results = [ deepcopy(grammar) ]

        exp_non_terminals = set('SAB')
        exp_terminals = set('ab')
        exp_productions = {
            Prod('S', ('a', 'A', 'B')),
            Prod('S', ('B',)),
            Prod('A', ('a', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,))
        }
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)
        results.append(exp_grammar)

        exp_productions = {
            Prod('S', ('a', 'A', 'B')),
            Prod('S', ('b', 'B',)),
            Prod('A', ('a', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
            Prod('B', (Grammar.EPSILON,))
        }
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)
        results.append(exp_grammar)

        grammar.remove_left_recursion()
        self.assertIn(grammar, results)

    def test_get_direct_left(self):
        non_terminals = set('ETF')
        terminals = set('+*()') | { 'id' }
        productions = {
            Prod('E', ('E','+','T')),
            Prod('E', ('T',)),
            Prod('T', ('T','*','F')),
            Prod('T', ('F',)),
            Prod('F', ('(','E',')')),
            Prod('F', ('id',))
        }
        start = 'E'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar._get_direct_left()
        expected = set('ET')
        self.assertSetEqual(result, expected)

    def test_get_direct_left2(self):
        non_terminals = { 'S' }
        terminals = set('ab')
        productions = {
            Prod('S', ('S','a')),
            Prod('S', ('b',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar._get_direct_left()
        expected = { 'S' }
        self.assertSetEqual(result, expected)

    def test_get_indirect_left(self):
        non_terminals = set('SABC')
        terminals = set('abcd')
        productions = {
            Prod('S', ('A','B')),
            Prod('S', ('B','C')),
            Prod('A', ('a','A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b','B')),
            Prod('B', ('d',)),
            Prod('C', ('c','C')),
            Prod('C', ('c',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar._get_indirect_left()
        expected = set()
        self.assertSetEqual(result, expected)

    def test_get_indirect_left2(self):
        non_terminals = set('SB')
        terminals = set('abd')
        productions = {
            Prod('S', ('a','S')),
            Prod('S', ('a','B')),
            Prod('S', ('d','S')),
            Prod('B', ('b','B')),
            Prod('B', ('b',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar._get_indirect_left()
        expected = set()
        self.assertSetEqual(result, expected)

    def test_get_indirect_left3(self):
        non_terminals = set('SA')
        terminals = set('ac')
        productions = {
            Prod('S', ('a','S')),
            Prod('S', ('A',)),
            Prod('A', ('a','A','c')),
            Prod('A', (Grammar.EPSILON,))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)

        result = grammar._get_indirect_left()
        expected = set()
        self.assertSetEqual(result, expected)

    def test_remove_direct_left_recursion(self):
        non_terminals = { 'S' }
        terminals = set('ab')
        productions = {
            Prod('S', ('S','a')),
            Prod('S', ('b',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_direct_left_recursion('S')

        exp_non_terminals = { 'S', 'S0' }
        exp_terminals = set('ab')
        exp_productions = {
            Prod('S', ('b','S0')),
            Prod('S0', ('a','S0')),
            Prod('S0', (Grammar.EPSILON,))
        }
        exp_start = 'S'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)

        self.assertEqual(grammar, exp_grammar)

    def test_remove_direct_left_recursion2(self):
        non_terminals = set('ETF')
        terminals = set('+*()') | { 'id' }
        productions = {
            Prod('E', ('E','+','T')),
            Prod('E', ('T',)),
            Prod('T', ('T','*','F')),
            Prod('T', ('F',)),
            Prod('F', ('(','E',')')),
            Prod('F', ('id',))
        }
        start = 'E'
        grammar = Grammar(non_terminals, terminals, productions, start)
        left_recursive_symbols = grammar._get_direct_left()
        for symbol in left_recursive_symbols:
            grammar.remove_direct_left_recursion(symbol)

        exp_non_terminals = { 'E', 'E0', 'T', 'T0', 'F' }
        exp_terminals = set('+*()') | { 'id' }
        exp_productions = {
            Prod('E', ('T','E0')),
            Prod('E0', ('+','T','E0')),
            Prod('E0', (Grammar.EPSILON,)),
            Prod('T', ('F','T0')),
            Prod('T0', ('*','F','T0')),
            Prod('T0', (Grammar.EPSILON,)),
            Prod('F', ('(','E',')')),
            Prod('F', ('id',))
        }
        exp_start = 'E'
        exp_grammar = Grammar(
            exp_non_terminals,
            exp_terminals,
            exp_productions,
            exp_start)
        self.assertEqual(grammar, exp_grammar)

    def test_remove_direct_left_recursion3(self):
        non_terminals = { 'S1' }
        terminals = set('ab')
        productions = {
            Prod('S1', ('S1', 'a')),
            Prod('S1', ('b',))
        }
        start = 'S1'
        grammar = Grammar(non_terminals, terminals, productions, start)

        expected_non_terminals = { 'S1', 'S0' }
        expected_terminals = set('ab')
        expected_productions = {
            Prod('S1', ('b', 'S0')),
            Prod('S0', ('a', 'S0')),
            Prod('S0', (Grammar.EPSILON,))
        }
        expected_start = 'S1'
        exp_grammar = Grammar(
            expected_non_terminals,
            expected_terminals,
            expected_productions,
            expected_start)

        grammar.remove_direct_left_recursion('S1')
        self.assertEqual(grammar, exp_grammar)

    def test_remove_left_recursion(self):
        non_terminals = set('SA')
        terminals = set('abcd')
        productions = {
            Prod('S', ('A','a')),
            Prod('S', ('S','b')),
            Prod('A', ('S','c')),
            Prod('A', ('d',))
        }
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_left_recursion()

        exp_non_terminals1 = { 'S', 'S0', 'A', 'A0' }
        exp_terminals1 = set('abcd')
        exp_productions1 = {
            Prod('S', ('A','a','S0')),
            Prod('S0', ('b','S0')),
            Prod('S0', (Grammar.EPSILON,)),
            Prod('A', ('d','A0')),
            Prod('A0', ('a','S0','c','A0')),
            Prod('A0', (Grammar.EPSILON,))
        }
        exp_start1 = 'S'
        exp1 = Grammar(exp_non_terminals1, exp_terminals1, exp_productions1, exp_start1)

        exp_non_terminals2 = { 'S', 'S0', 'A' }
        exp_terminals2 = set('abcd')
        exp_productions2 = {
            Prod('S0', ('c','a','S0')),
            Prod('S0', ('b','S0')),
            Prod('S0', (Grammar.EPSILON,)),
            Prod('S', ('d','a','S0')),
            Prod('A', ('S','c')),
            Prod('A', ('d',))
        }
        exp_start2 = 'S'
        exp2 = Grammar(exp_non_terminals2, exp_terminals2, exp_productions2, exp_start2)

        exp_answers = [exp1, exp2]
        self.assertIn(grammar, exp_answers)
        # assert False
