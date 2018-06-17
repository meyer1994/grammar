import re
from itertools import combinations

from grammar.production import Prod


class Grammar(object):

    EPSILON = '&'

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
        unreachable = (self.terminals | self.non_terminals) - self.reachable()
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
        closure = self._closure(self.start)
        self._remove_productions_with_symbol(Grammar.EPSILON)

        new_prods = set()
        for prod in self.productions:
            # Generate possible combinations of the epslon set symbols
            for comb in Grammar.epsilon_combinations(prod, closure):
                new_prod = list(prod.p)
                for c in comb:
                    new_prod[c[0]] = ''
                new_prod = (prod.n, ''.join(new_prod))
                new_prods.add(new_prod)

        # Add created productions to grammar
        for non_terminal, production in new_prods:
            if production:
                self.add_production(non_terminal, production)

        if self.start not in closure:
            return

        # S' -> S | epsilon
        new_start = self.start + "'"
        self.non_terminals.add(new_start)
        self.add_production(new_start, self.start)
        self.add_production(new_start, Grammar.EPSILON)
        self.start = new_start

    def is_empty(self):
        '''
        Checks if the language generated by this grammar is empty or not.
        '''
        productive_symbols = self.productive()
        return self.start not in productive_symbols

    def productive(self):
        '''
        Gets the set of productive symbols of the grammar.
        '''
        old_set = set()
        while True:
            # Ni
            new_set = set()

            # (Ni-1 U Vt)*
            union = old_set | self.terminals | set(Grammar.EPSILON)

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

    def reachable(self):
        '''
        Gets the set of reachable symbols from the start symbol.
        '''
        # (Vn U Vt)*
        union = self.non_terminals | self.terminals | set(Grammar.EPSILON)

        old_set = set(self.start)
        while True:
            # Ni
            new_set = set()

            for (non_term, prod) in self.productions:
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
            if item in epsilon_set:
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

    def _closure(self, start, symbol=EPSILON):
        '''
        Gets the non terminal symbols that derive EPSILON in 0 or more
        derivations
        '''
        old_set = set()
        while True:
            # Ni
            new_set = set()

            # (Ni-1 U epsilon)*
            union = old_set | set(Grammar.EPSILON)

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

    def _get_productions_by_non_terminal(self, non_terminal):
        '''
        Returns a list of the productions from the passed non terminal.
        '''
        return [ p for n, p in self.productions if n == non_terminal ]

    def __eq__(self, other):
        vnt = self.non_terminals == other.non_terminals
        vt = self.terminals == other.terminals
        prods = self.productions == other.productions
        start = self.start == other.start
        return vnt and vt and prods and start

    def __str__(self):
        lines = []
        for non_terminal in self.non_terminals:
            productions = self._get_productions_by_non_terminal(non_terminal)
            line = f'{non_terminal} ->'
            for p in productions:
                line += f' {p} |'
            line = line[:-2]
            lines.append(line)

        # Makes start symbol come first
        # The previous implementation used a loop. But, because of the
        # non-deterministic nature of sets, sometimes the coverage of the tests
        # where not 100%
        lines_starts = map(lambda l: l.split(' -> ')[0], lines)
        start_symbol_index = list(lines_starts).index(self.start)
        start_line = lines.pop(start_symbol_index)
        lines.insert(0, start_line)

        return '\n'.join(lines)
