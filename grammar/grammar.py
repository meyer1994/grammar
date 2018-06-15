from grammar.production import Prod


class Grammar(object):

    EPSILON = '&'

    def __init__(self, non_terminals, terminals, productions, start):
        super(Grammar, self).__init__()
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start = start

    def remove_non_terminal(self, symbol):
        self.non_terminals.discard(symbol)
        self._remove_productions_with_symbol(symbol)

    def remove_terminal(self, symbol):
        self.terminals.discard(symbol)
        self._remove_productions_with_symbol(symbol)

    def remove_unproductive(self):
        unproductive_symbols = self.non_terminals - self.productive()
        for symbol in unproductive_symbols:
            self.remove_non_terminal(symbol)

    def is_empty(self):
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

    def _remove_productions_with_symbol(self, symbol):
        # We use a list here because we cannot change set size while iterating
        # over it
        prods_to_remove = []
        for prod in self.productions:
            if prod.n == symbol or symbol in prod.p:
                prods_to_remove.append(prod)

        for prod in prods_to_remove:
            self.productions.discard(prod)
