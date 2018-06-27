import re
from itertools import combinations
from collections import defaultdict
from copy import deepcopy
from pprint import pprint

from grammar.production import Prod

class Grammar(object):

    EPSILON = '&'
    FINISH = '$'

    def __init__(self, non_terminals, terminals, productions, start):
        super(Grammar, self).__init__()
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start = start

    def add_production(self, non_terminal, production):
        self.productions.add(Prod(non_terminal, production))

    def remove_non_terminal(self, symbol):
        '''
        Remove non terminal symbol from grammar.
        '''
        self.non_terminals.discard(symbol)
        self._remove_productions_with_symbol(symbol)

    def remove_terminal(self, symbol):
        '''
        Remove terminal symbol from grammar.
        '''
        self.terminals.discard(symbol)
        self._remove_productions_with_symbol(symbol)

    def remove_unproductive(self):
        '''
        Remove the unproductive symbols from the grammar.
        '''
        unproductive = self.non_terminals - self.productive()
        for symbol in unproductive:
            self.remove_non_terminal(symbol)

    def remove_unreachable(self):
        '''
        Remove all unreachable symbols from the grammar.
        '''
        unreachable = self.terminals | self.non_terminals
        unreachable -= self.reachable(self.start)
        for symbol in unreachable:
            if symbol in self.terminals:
                self.remove_terminal(symbol)

            if symbol in self.non_terminals:
                self.remove_non_terminal(symbol)

    def remove_useless(self):
        '''
        Remove useless symbols.
        '''
        self.remove_unproductive()
        self.remove_unreachable()

    def remove_epsilon(self):
        '''
        Transforms the grammar into a epslon free grammar.
        '''
        # Ne
        closure = self._epsilon_closure()
        self._remove_productions_with_symbol(Grammar.EPSILON)

        new_prods = set()
        for prod in self.productions:
            # Generate possible combinations of the epslon set symbols
            for comb in Grammar.epsilon_combinations(prod, closure):
                new_prod = list(prod.p)
                for c, _ in comb:
                    new_prod[c] = ''
                new_prod = filter(lambda i: i != '', new_prod)
                new_prods.add((prod.n, tuple(new_prod)))

        # Add created productions to grammar
        for non_terminal, production in new_prods:
            if production:
                self.add_production(non_terminal, production)

        if (self.start,) not in closure:
            return

        # S' -> S | epsilon
        new_start = self._get_next_nt(self.start)
        self.non_terminals.add(new_start)
        self.add_production(new_start, (self.start,))
        self.add_production(new_start, (Grammar.EPSILON,))
        self.start = new_start

    def remove_simple(self):
        '''
        Remove simple productions from the grammar.
        '''
        simple_table = self.simple_table()

        self._remove_simple_productions()

        for symbol, simple in simple_table.items():
            for non_terminal in simple:
                for prod in self[non_terminal]:
                    self.add_production(symbol, prod)

    def simple_table(self):
        return { s: self._symbol_simple(s) for s in self.non_terminals }

    def remove_direct_left_recursion(self, symbol):
        direct = { p for p in self[symbol] if p[0] == symbol }
        no_recursion = { p for p in self[symbol] if p[0] != symbol }

        # No direct recursion
        if len(direct) == 0:
            return

        # Remove prods
        for p in self[symbol]:
            self.productions.discard((symbol, p))

        # Create new nt
        new_symbol = self._get_next_nt(symbol)
        self.non_terminals.add(new_symbol)

        for prod in no_recursion:
            self.add_production(symbol, prod + (new_symbol,))

        for prod in direct:
            self.add_production(new_symbol, prod[1:] + (new_symbol,))
        self.add_production(new_symbol, (Grammar.EPSILON,))

    def remove_left_recursion(self):
        ordered_vn = [ i for i in self.non_terminals ]

        for i, ai in enumerate(ordered_vn):
            for j in range(i):
                aj = ordered_vn[j]
                prods_ai_to_aj = { (ai, p) for p in self[ai] if p[0] == aj }
                for p in prods_ai_to_aj:
                    self.productions.discard(p)

                aj_prods = self[aj]
                for _, ai_prod in prods_ai_to_aj:
                    for aj_prod in aj_prods:
                        if aj_prod == (Grammar.EPSILON,):
                            new_prod = ai_prod[1:]
                        else:
                            new_prod = aj_prod + ai_prod[1:]

                        if new_prod:
                            self.add_production(ai, new_prod)

            self.remove_direct_left_recursion(ai)

    def is_empty(self):
        '''
        Checks if the language generated by this grammar is empty or not.
        '''
        productive_symbols = self.productive()
        return self.start not in productive_symbols

    def is_finite(self):
        tmp_grammar = Grammar(
            self.non_terminals.copy(),
            self.terminals.copy(),
            self.productions.copy(),
            self.start)

        # Proper
        tmp_grammar.remove_epsilon()
        tmp_grammar.remove_simple()
        tmp_grammar.remove_useless()

        # Create reachable table, only non-terminals
        table = {}
        for nt in tmp_grammar.non_terminals:
            table[nt] = tmp_grammar.reachable(nt) - tmp_grammar.terminals

        for nt in tmp_grammar.non_terminals:
            visited = set()
            stack = [ nt ]
            while len(stack) > 0:
                item = stack.pop()
                for prod in tmp_grammar[item]:
                    non_term = set(prod) - tmp_grammar.terminals
                    for n in non_term:
                        if n in visited:
                            return False
                        visited.add(n)
                        stack.append(n)
        return True

    def is_factored(self):
        '''
        Checks if the grammar is factored or not.

        It does so by intersecting the first sets of the productions of each
        non terminal.
        '''
        factors = ( self._get_factors(n) for n in self.non_terminals )
        for fact in factors:
            factorables = filter(lambda f: len(f) > 1, fact)
            factorables = list(factorables)
            if factorables:
                return False
        return True

    def factor(self, steps=1):
        grammar = deepcopy(self)

        while steps:
            factors = {}
            for nt in grammar.non_terminals:
                factors[nt] = grammar._get_factors(nt)
                factors[nt] = filter(lambda f: len(f) > 1, factors[nt])

            for nt, factor in factors.items():
                for f in factor:
                    if steps == 0:
                        return False
                    grammar._factor(nt, f)
                    steps -= 1
                if grammar.is_factored():
                    return grammar

        return False

    def _get_factors(self, nt):
        '''
        Gets the productions by a non-terminal that can be factored.
        '''
        first = self.first_sets()
        prods = self[nt]
        factors = []

        while prods:
            p1 = prods.pop()
            prod_set = set([ p1 ])
            p1_set = self._first_sequence(first, p1)
            for p2 in prods:
                p2_set = self._first_sequence(first, p2)
                intersection = (p1_set & p2_set) - { Grammar.EPSILON }
                if intersection:
                    prod_set.add(p2)

            prods -= prod_set
            factors.append(prod_set)

        return factors

    def _factor(self, nt, factors):
        '''
        Factor the productions passed.
        '''
        # Create new non terminal
        new_nt = self._get_next_nt(nt)
        self.non_terminals.add(new_nt)

        # Get factorable part
        factor_part = self._get_factor_part(factors)

        # Remove productions
        for f in factors:
            self.productions.discard(Prod(nt, f))

        # Add production to original non terminal
        factor_part.append(new_nt)
        self.add_production(nt, tuple(factor_part))

        # Add non factorable part of prods to new non terminal
        factor_size = len(factor_part) - 1 # we added the new_nt
        for fact in factors:
            fact = list(fact)[factor_size:]
            if fact:
                self.add_production(new_nt, tuple(fact))
            else:
                self.add_production(new_nt, (Grammar.EPSILON,))

    def _get_factor_part(self, factors):
        '''
        Returns the factorable part of productions.
        '''
        smallest_size = min(map(lambda i: len(i), factors))

        base_prod = factors.pop()
        factors.add(base_prod)

        factor_part = []
        for i in range(smallest_size):
            symbol = base_prod[i]
            for factor in factors:
                if factor[i] != symbol:
                    return factor_part
            factor_part.append(symbol)
        return factor_part

    def _get_next_nt(self, nt):
        '''
        Gets the next possible non-terminal to be created.
        '''
        nt = nt[0]

        non_terminals = { n for n in self.non_terminals if len(n) > 1 }
        non_terminals = { n for n in non_terminals if n[0] == nt }

        counter = 0
        while True:
            new_nt = f'{nt}{counter}'
            if new_nt not in non_terminals:
                return new_nt
            counter += 1

    def productive(self):
        '''
        Gets the set of productive symbols of the grammar.
        '''
        old_set = set()
        while True:
            # Ni
            new_set = set()

            # (Ni-1 U Vt)*
            union = old_set | self.terminals | { Grammar.EPSILON }

            for (non_term, prod) in self.productions:
                # alpha contained in (Ni-1 U Vt)*
                if set(prod) <= union:
                    new_set.add(non_term)

            # Ni-1 U new_set
            new_set |= old_set

            if new_set == old_set:
                break

            old_set = new_set

        return old_set

    def reachable(self, symbol):
        '''
        Gets the set of reachable symbols from the symbol.
        '''
        # (Vn U Vt)*
        union = self.non_terminals | self.terminals | { Grammar.EPSILON }

        old_set = { symbol }
        while True:
            # Ni
            new_set = set()

            for non_term, prod in self.productions:
                # A in Vi-1
                if non_term not in old_set:
                    continue

                # alpha, beta contained in (Vn U Vt)*
                new_set |= set(prod)

            # Ni-1 U new_set
            new_set |= old_set

            if new_set == old_set:
                break

            old_set = new_set

        return old_set

    def first_sets(self):
        first = self._first()
        for val in first.values():
            val -= self.non_terminals
        return first

    def first_NT(self):
        first = self._first()
        for first_set in first.values():
            first_set -= self.terminals | { Grammar.EPSILON }

        for symbol in self.terminals:
            first.pop(symbol)
        return first

    def _first(self):
        first_dict = defaultdict(set)
        # Rule 1
        for symbol in self.terminals:
            first_dict[symbol].add(symbol)

        while True:
            new_dict = deepcopy(first_dict)

            for symbol in self.non_terminals:
                productions = self[symbol]

                # Rule 2
                to_discard = set()
                for prod in productions:
                    first = prod[0]
                    if first in self.terminals:
                        new_dict[symbol].add(first)
                        to_discard.add(prod)
                productions -= to_discard

                # Rule 3
                for prod in productions:
                    first_seq = self._first_sequence(new_dict, prod)
                    new_dict[symbol] |= first_seq

            if new_dict == first_dict:
                break

            first_dict = new_dict

        return dict(first_dict)

    def follow_sets(self):
        follow = defaultdict(set)
        first = self.first_sets()

        while True:
            new_follow = deepcopy(follow)

            for nt in self.non_terminals:

                # Rule 1
                if nt == self.start:
                    new_follow[nt].add(Grammar.FINISH)

                productions = self[nt]

                # Rule 2
                for prod in productions:
                    seq = list(prod)
                    while seq:
                        symbol = seq.pop(0)
                        # Go until the second-to-last symbol
                        if not seq:
                            break

                        if symbol in self.terminals:
                            continue

                        seq_first = self._first_sequence(first, seq)
                        new_follow[symbol] |= seq_first - self.non_terminals

                # Rule 3
                for prod in productions:
                    seq = list(prod)
                    while seq:
                        symbol = seq.pop(0)
                        if symbol in self.terminals | { Grammar.EPSILON }:
                            continue

                        if not seq:
                            new_follow[symbol] |= new_follow[nt]
                            break

                        if Grammar.EPSILON in self._first_sequence(first, seq):
                            new_follow[symbol] |= new_follow[nt]


            if new_follow == follow:
                break

            follow = new_follow

        # We add EPSILON for simplicity, but it does not make much sense, so
        # we filter it out
        for val in follow.values():
            val.discard(Grammar.EPSILON)

        return dict(follow)

    def _first_sequence(self, first, sequence):
        first_set = set()
        seq = list(sequence)
        while seq:
            symbol = seq.pop(0)

            if symbol in self.terminals | { Grammar.EPSILON }:
                first_set.add(symbol)
                break

            first_set |= first[symbol]
            first_set.add(symbol)
            if Grammar.EPSILON not in first[symbol]:
                break

            if seq:
                first_set.discard(Grammar.EPSILON)

        return first_set

    def has_direct_left_recursion(self):
        direct = self._get_direct_left()
        return len(direct) > 0

    def _get_direct_left(self):
        return { p.n for p in self.productions if p.n == p.p[0] }

    def has_indirect_left_recursion(self):
        indirect = self._get_indirect_left()
        return len(indirect) > 0

    def _get_indirect_left(self):
        indirect = set()
        first = self._first()

        for nt in self.non_terminals:
            not_direct = { p for p in self[nt] if p[0] != nt }

            for prod in not_direct:
                prod_first = self._first_sequence(first, prod)
                if nt in prod_first:
                    indirect.add(nt)

        return indirect

    def has_left_recursion(self):
        direct = self._get_direct_left()
        indirect = self._get_indirect_left()
        return len(direct | indirect) > 0

    @staticmethod
    def epsilon_combinations(prod, epsilon_set):
        '''
        Used internally to get the indexes of the non terminals that must be
        removed when removing epsilon.

        It takes the positions of each symbol that is in the set and makes all
        the possible combinations of it.
        '''
        non_terminal, production = prod

        # Gets symbols and indexes
        epsilon_positions = []
        for i, item in enumerate(production):
            if (item,) in epsilon_set:
                epsilon_positions.append((i, item))

        # All possible combinations
        for i, _ in enumerate(epsilon_positions):
            for item in combinations(epsilon_positions, i + 1):
                yield item

    def _remove_productions_with_symbol(self, symbol):
        # We use a list here because we cannot change set size while iterating
        # over it
        prods_to_remove = []
        for prod in self.productions:
            if prod.n == symbol or symbol in prod.p:
                prods_to_remove.append(prod)

        for prod in prods_to_remove:
            self.productions.discard(prod)

    def _epsilon_closure(self):
        '''
        Gets the non terminal symbols that derive EPSILON in 0 or more
        derivations
        '''
        old_set = set()
        while True:
            # Ni
            new_set = set()

            # (Ni-1 U epsilon)*
            union = old_set | { (Grammar.EPSILON,) }

            for (non_term, prod) in self.productions:
                prods = ( (i,) for i in prod )
                # alpha contained in (Ni-1 U Vt)*
                if set(prods) <= union:
                    new_set.add((non_term,))

            # Ni-1 U new_set
            new_set |= old_set

            if new_set == old_set:
                break

            old_set = new_set

        return old_set

    def _remove_simple_productions(self):
        '''
        Remove all simple productions from the productions set.

        It is done this way, by creating a separate set, because python throws
        an error when changing the set size during iterations.
        '''
        to_remove = set()
        for prod in self.productions:
            if self._is_simple_prod(prod.p):
                to_remove.add(prod)

        for prod in to_remove:
            self.productions.discard(prod)

    def _symbol_simple(self, symbol):
        '''
        Gets the set of symbols that are derived only in simple productions.

        A simple production is a production of the form:
            { A -> B | A, B are non terminals }
        '''
        visited = { symbol }
        stack = [ symbol ]

        while len(stack) > 0:
            symbol = stack.pop()
            for prod in self[symbol]:
                if self._is_simple_prod(prod) and prod[0] not in visited:
                    stack.append(prod[0])
                    visited.add(prod[0])

        return visited

    def _is_simple_prod(self, p):
        '''
        Checks if some production is simple.
        '''
        return len(p) == 1 and p[0] in self.non_terminals

    def _to_line(self, nt):
        productions = self[nt]
        line = f'{nt} ->'
        for p in productions:
            prod = ' '.join(p)
            line += f' {prod} |'
        line = line[:-2]
        return line

    def __eq__(self, other):
        vnt = self.non_terminals == other.non_terminals
        vt = self.terminals == other.terminals
        prods = self.productions == other.productions
        start = self.start == other.start
        return vnt and vt and prods and start

    def __str__(self):
        lines = [ self._to_line(self.start) ]
        for non_terminal in self.non_terminals - { self.start }:
            line = self._to_line(non_terminal)
            lines.append(line)

        return '\n'.join(lines)

    def __getitem__(self, nt):
        '''
        Returns a list of the productions from the passed non terminal.
        '''
        return { p for n, p in self.productions if n == nt }

