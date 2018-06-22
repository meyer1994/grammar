import re
from itertools import combinations
from collections import defaultdict
from pprint import pprint

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
        unreachable = (self.terminals | self.non_terminals)
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
        new_start = self.start + "'"
        self.non_terminals.add(new_start)
        self.add_production(new_start, (self.start,))
        self.add_production(new_start, (Grammar.EPSILON,))
        self.start = new_start

    def remove_simple(self):
        '''
        Remove simple productions from the grammar.
        '''
        simple_table = {}
        for symbol in self.non_terminals:
            simple_table[symbol] = self._symbol_simple(symbol)

        self._remove_simple_productions()

        for symbol, simple in simple_table.items():
            for non_terminal in simple:
                for prod in self._get_productions_by_non_terminal(non_terminal):
                    self.add_production(symbol, prod)

    def remove_direct_left_recursion(self, symbol):
        prods_to_add = []
        prods_to_remove = []
        count = 1
        for prod in self.productions:
            if prod.n == symbol:
                while True:
                    if (symbol[0] + str(count)) in self.non_terminals:
                        count += 1
                    else:
                        break

                if prod.p[0] == symbol:
                    prods_to_add.append(Prod(symbol[0] + str(count), prod.p[1:] + (symbol[0] + str(count),) ))
                    prods_to_remove.append(prod)
                else:
                    prods_to_add.append(Prod(symbol, prod.p + (symbol[0] + str(count),) ))
                    prods_to_remove.append(prod)

        self.non_terminals.add(symbol[0] + str(count))
        self.productions.add(Prod(symbol[0] + str(count), (Grammar.EPSILON,)))
        for prod in prods_to_remove:
            self.productions.discard(prod)
        for prod in prods_to_add:
            self.productions.add(prod)

    def remove_left_recursion(self):
        symbols_with_direct_left_recursion = self.has_direct_left_recursion()
        #order vn
        ordered_vn = dict(zip(range(len(self.non_terminals)), self.non_terminals))
        for i in range(len(ordered_vn)):
            for j in range(0, i):
                prods_to_remove = []
                prods_to_add = []
                for prod in self.productions:
                    if prod.n == ordered_vn[i] and prod.p[0] == ordered_vn[j]:
                        prods_to_remove.append(prod)
                        for (vn, production) in self.productions:
                            if vn == ordered_vn[j]:
                                prods_to_add.append(Prod(ordered_vn[i], production + prod.p[1:]))

                for prod in prods_to_remove:
                    self.productions.discard(prod)
                for prod in prods_to_add:
                    self.productions.add(prod)
                    if prod.n == prod.p[0]:
                        symbols_with_direct_left_recursion.add(prod.n)

            if ordered_vn[i] in symbols_with_direct_left_recursion:
                self.remove_direct_left_recursion(ordered_vn[i])

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
        # tmp_grammar.remove_epsilon()
        tmp_grammar.remove_useless()
        # tmp_grammar.remove_simple()


        visited = set([ tmp_grammar.start ])
        stack = [ tmp_grammar.start ]
        while len(stack) > 0:
            item = stack.pop()
            reachable = self.reachable(item) - tmp_grammar.terminals
            reachable.discard(item)
            if any(i in visited for i in reachable):
                return True
            for i in reachable:
                stack.append(i)
                visited.add(i)
        return False

    def is_factored(self):
        '''
        Checks if the grammar is factored or not
        '''
        for non_terminal in self.non_terminals:
            productions = self._get_productions_by_non_terminal(non_terminal)
            visited = set()
            for production in productions:
                if production[0] in visited:
                    return False
                visited.add(production[0])
        return True

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

    def reachable(self, symbol):
        '''
        Gets the set of reachable symbols from the symbol.
        '''
        # (Vn U Vt)*
        union = self.non_terminals | self.terminals | set(Grammar.EPSILON)

        old_set = set(symbol)
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

    def first_and_follow(self):
        first = {i: set() for i in self.non_terminals}
        first.update((i, {i}) for i in self.terminals)
        follow = {i: set() for i in self.non_terminals}
        follow[self.start].add('$')
        first_NT = {i: set() for i in self.non_terminals}
        epsilon = set()

        while True:
            updated = False

            for nt, expression in self.productions:
                for symbol in expression:
                    if symbol == Grammar.EPSILON:
                        updated |= self._union(epsilon, {nt})
                        continue
                    else:
                        # FIRST
                        updated |= self._union(first[nt], first[symbol])
                        # FIRST_NT
                        if symbol in first_NT:
                            updated |= self._union(first_NT[nt], {symbol})
                            updated |= self._union(first_NT[nt], first_NT[symbol])
                        if symbol not in epsilon:
                            break
                else:
                    updated |= self._union(epsilon, {nt})

                aux = follow[nt]
                for symbol in reversed(expression):
                    if symbol == Grammar.EPSILON:
                        break
                    if symbol in follow:
                        updated |= self._union(follow[symbol], aux)
                    if symbol in epsilon:
                        aux = aux.union(first[symbol])
                    else:
                        aux = first[symbol]

            if not updated:
                for nt in epsilon:
                    first[nt].add(Grammar.EPSILON)
                return first, follow, first_NT

    def has_direct_left_recursion(self):
        non_terminal_with_left_recursion = set()
        for prod in self.productions:
            if prod.n == prod.p[0]:
                non_terminal_with_left_recursion.add(prod.n)
        return non_terminal_with_left_recursion

    def has_indirect_left_recursion(self):
        non_terminal_with_left_recursion = set()
        # Gramatica tem que ser propria?
        # (Vn U Vt)*
        # union = self.non_terminals | self.terminals | set(Grammar.EPSILON)
        for non_terminal_symbol in self.non_terminals:
            old_set = set()
            # get all the non_terminal symbols that are in the most left side of the prod
            for (non_term, prod) in self.productions:
                if non_term == non_terminal_symbol and prod[0] in self.non_terminals:
                    old_set.add(prod[0])
            old_set.discard(non_terminal_symbol)
            while True:
                # Ni
                new_set = set()

                for (non_term, prod) in self.productions:
                    # A in Vi-1
                    if non_term not in old_set:
                        continue

                    # B.beta type production
                    if prod[0] in self.non_terminals:
                        new_set.add(prod[0])

                # Ni-1 U new_set
                new_set |= old_set

                if new_set == old_set:
                    break

                old_set = new_set

            if non_terminal_symbol in old_set:
                non_terminal_with_left_recursion.add(non_terminal_symbol)

        return non_terminal_with_left_recursion

    def has_left_recursion(self):
        direct = self.has_direct_left_recursion()
        indirect = self.has_indirect_left_recursion()
        return direct or indirect

    def _union(self, first, begins):
        n = len(first)
        first |= begins
        return len(first) != n

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
            union = old_set | set([ (Grammar.EPSILON,) ])

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

    def _get_productions_by_non_terminal(self, non_terminal):
        '''
        Returns a list of the productions from the passed non terminal.
        '''
        return [ p for n, p in self.productions if n == non_terminal ]

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
        new_set = set([ symbol ])

        for prod in self._get_productions_by_non_terminal(symbol):
            if self._is_simple_prod(prod):
                for i in self._symbol_simple(prod[0]):
                    new_set.add(i)

        return new_set

    def _is_simple_prod(self, prod):
        '''
        Checks if some production is simple.
        '''
        return len(prod) == 1 and prod[0] in self.non_terminals

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
                prod = ' '.join(p)
                line += f' {prod} |'
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
