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

        print(grammar)

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

    def test_remove_simple(self):
        non_terminals = set('SFGH')
        terminals = set('abcd')
        productions = set([
            Prod('S', ('F', 'G', 'H')),
            Prod('F', ('G',)),
            Prod('F', ('a',)),
            Prod('G', ('d', 'G')),
            Prod('G', ('H',)),
            Prod('G', ('b',)),
            Prod('H', ('c',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_simple()

        exp_non_terminals = set('SFGH')
        exp_terminals = set(grammar.terminals)
        exp_productions = set([
            Prod('S', ('F', 'G', 'H')),
            Prod('F', ('a',)),
            Prod('F', ('d', 'G')),
            Prod('F', ('b',)),
            Prod('F', ('c',)),
            Prod('G', ('d', 'G')),
            Prod('G', ('b',)),
            Prod('G', ('c',)),
            Prod('H', ('c',))
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

        result = grammar.reachable(start)
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

        result = grammar._epsilon_closure()
        expected = set([ (i,) for i in 'SAB' ])

        self.assertSetEqual(result, expected)

    def test_symbol_simple(self):
        non_terminals = set('SFGH')
        terminals = set('abcd')
        productions = set([
            Prod('S', ('F', 'G', 'H')),
            Prod('F', ('G',)),
            Prod('F', ('a',)),
            Prod('G', ('d', 'G')),
            Prod('G', ('H',)),
            Prod('G', ('b',)),
            Prod('H', ('c',))
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)


        result = [ grammar._symbol_simple(i) for i in 'SFGH' ]
        expected = [ set('S'), set('FGH'), set('GH'), set('H')  ]

        for i, _ in enumerate(result):
            self.assertSetEqual(result[i], expected[i])

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
            Prod('S', ('A', 'B')),
            Prod('A', ('a', 'A')),
            Prod('A', (Grammar.EPSILON,)),
            Prod('B', ('b', 'B')),
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
    def test_has_direct_left_recursion_true(self):
        non_terminals = set('S')
        terminals = set('ab')
        productions = set([
            Prod('S', 'Sa'),
            Prod('S', 'b')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        bool_response, left_recursive_symbols = grammar.has_direct_left_recursion()
        self.assertTrue(bool_response)
        self.assertEqual(left_recursive_symbols, set('S'))

        non_terminals = set('ETF')
        terminals = set('+*()')
        terminals.add('id')
        productions = set([
            Prod('E', 'E+T'),
            Prod('E', 'T'),
            Prod('T', 'T*F'),
            Prod('T', 'F'),
            Prod('F', '(E)'),
            Prod('F', 'id')
        ])
        start = 'E'
        grammar = Grammar(non_terminals, terminals, productions, start)
        bool_response, left_recursive_symbols = grammar.has_direct_left_recursion()
        self.assertTrue(bool_response)
        self.assertEqual(left_recursive_symbols, set('ET'))

    def test_has_direct_left_recursion_false(self):
        non_terminals = set('SABC')
        terminals = set('abcd')
        productions = set([
            Prod('S', 'AB'),
            Prod('S', 'BC'),
            Prod('A', 'aA'),
            Prod('A', Grammar.EPSILON),
            Prod('B', 'bB'),
            Prod('B', 'd'),
            Prod('C', 'cC'),
            Prod('C', 'c')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        bool_response, left_recursive_symbols = grammar.has_direct_left_recursion()
        self.assertFalse(bool_response)
        self.assertEqual(left_recursive_symbols, set())

        non_terminals = set('SB')
        terminals = set('abd')
        productions = set([
            Prod('S', 'aS'),
            Prod('S', 'aB'),
            Prod('S', 'dS'),
            Prod('B', 'bB'),
            Prod('B', 'b')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        bool_response, left_recursive_symbols = grammar.has_direct_left_recursion()
        self.assertFalse(bool_response)
        self.assertEqual(left_recursive_symbols, set())

        non_terminals = set('SA')
        terminals = set('ac')
        productions = set([
            Prod('S', 'aS'),
            Prod('S', 'A'),
            Prod('A', 'aAc'),
            Prod('A', Grammar.EPSILON)
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        bool_response, left_recursive_symbols = grammar.has_direct_left_recursion()
        self.assertFalse(bool_response)
        self.assertEqual(left_recursive_symbols, set())

    def test_remove_direct_left_recursion(self):
        non_terminals = set('S')
        terminals = set('ab')
        productions = set([
            Prod('S', 'Sa'),
            Prod('S', 'b')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_direct_left_recursion('S')
        
        expected_non_terminals = set(['S', "S'"])
        expected_terminals = set('ab')
        expected_productions = set([
            Prod('S', "bS'"),
            Prod("S'", "aS'"),
            Prod("S'", Grammar.EPSILON)
        ])
        expected_start = 'S'
        exp_grammar = Grammar(
            expected_non_terminals,
            expected_terminals,
            expected_productions,
            expected_start)
        self.assertEqual(grammar, exp_grammar)
        # new example
        non_terminals = set('ETF')
        terminals = set('+*()')
        terminals.add('id')
        productions = set([
            Prod('E', 'E+T'),
            Prod('E', 'T'),
            Prod('T', 'T*F'),
            Prod('T', 'F'),
            Prod('F', '(E)'),
            Prod('F', 'id')
        ])
        start = 'E'
        grammar = Grammar(non_terminals, terminals, productions, start)
        left_recursive_symbols = grammar.has_direct_left_recursion()[1]
        for symbol in left_recursive_symbols:
            grammar.remove_direct_left_recursion(symbol)

        expected_non_terminals = set(['E', "E'", 'T', "T'", 'F'])
        expected_terminals = set('+*()')
        expected_terminals.add('id')
        expected_productions = set([
            Prod('E', "TE'"),
            Prod("E'", "+TE'"),
            Prod("E'", Grammar.EPSILON),
            Prod('T', "FT'"),
            Prod("T'", "*FT'"),
            Prod("T'", Grammar.EPSILON),
            Prod('F', '(E)'),
            Prod('F', 'id')
        ])
        expected_start = 'E'
        exp_grammar = Grammar(
            expected_non_terminals,
            expected_terminals,
            expected_productions,
            expected_start)
        self.assertEqual(grammar, exp_grammar)
    
    def test_has_indirect_left_recursion_true(self):
        non_terminals = set('SA')
        terminals = set('abcd')
        productions = set([
            Prod('S', 'Aa'),
            Prod('S', 'Sb'),
            Prod('A', 'Sc'),
            Prod('A', 'd')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        has_indirect, symbols_with_indirect_recursion = grammar.has_indirect_left_recursion()
        self.assertTrue(has_indirect)
        self.assertEqual(symbols_with_indirect_recursion, set('SA'))
        #test 2
        non_terminals = set('SAB')
        terminals = set('abcde')
        productions = set([
            Prod('S', 'aS'),
            Prod('S', 'Ab'),
            Prod('A', 'Ab'),
            Prod('A', 'Bc'),
            Prod('A', 'a'),
            Prod('B', 'Bd'),
            Prod('B', 'Sa'),
            Prod('B', 'e')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        has_indirect, symbols_with_indirect_recursion = grammar.has_indirect_left_recursion()
        self.assertTrue(has_indirect)
        self.assertEqual(symbols_with_indirect_recursion, set('SAB'))
    
    def test_has_indirect_left_recursion_false(self):
        non_terminals = set('S')
        terminals = set('ab')
        productions = set([
            Prod('S', 'Sa'),
            Prod('S', 'b')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        bool_response, left_recursive_symbols = grammar.has_indirect_left_recursion()
        self.assertFalse(bool_response)
        self.assertEqual(left_recursive_symbols, set())

        non_terminals = set('ETF')
        terminals = set('+*()')
        terminals.add('id')
        productions = set([
            Prod('E', 'E+T'),
            Prod('E', 'T'),
            Prod('T', 'T*F'),
            Prod('T', 'F'),
            Prod('F', '(E)'),
            Prod('F', 'id')
        ])
        start = 'E'
        grammar = Grammar(non_terminals, terminals, productions, start)
        bool_response, left_recursive_symbols = grammar.has_indirect_left_recursion()
        self.assertFalse(bool_response)
        self.assertEqual(left_recursive_symbols, set())
    
    def test_remove_left_recursion(self):
        non_terminals = set('SA')
        terminals = set('abcd')
        productions = set([
            Prod('S', 'Aa'),
            Prod('S', 'Sb'),
            Prod('A', 'Sc'),
            Prod('A', 'd')
        ])
        start = 'S'
        grammar = Grammar(non_terminals, terminals, productions, start)
        grammar.remove_left_recursion()

        exp_non_terminals1 = set(['S', "S'", 'A', "A'"])
        exp_terminals1 = set('abcd')
        exp_productions1 = set([
            Prod('S', "AaS'"),
            Prod("S'", "bS'"),
            Prod("S'", Grammar.EPSILON),
            Prod('A', "dA'"),
            Prod("A'", "aS'cA'"),
            Prod("A'", Grammar.EPSILON),
        ])
        exp_start1 = 'S'
        exp1 = Grammar(exp_non_terminals1, exp_terminals1, exp_productions1, exp_start1)

        exp_non_terminals2 = set(['S', "S'", 'A'])
        exp_terminals2 = set('abcd')
        exp_productions2 = set([
            Prod("S'", "caS'"),
            Prod("S'", "bS'"),
            Prod("S'", Grammar.EPSILON),
            Prod('S', "daS'"),
            Prod('A', 'Sc'),
            Prod('A', 'd')
        ])
        exp_start2 = 'S'
        exp2 = Grammar(exp_non_terminals2, exp_terminals2, exp_productions2, exp_start2)

        exp_answers = [exp1, exp2]
        self.assertIn(grammar, exp_answers)
