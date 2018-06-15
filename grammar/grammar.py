from grammar.production import Prod


class Grammar(object):

    EPSILON = '&'

    def __init__(self, non_terminals, terminals, productions, start):
        super(Grammar, self).__init__()
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start = start

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
