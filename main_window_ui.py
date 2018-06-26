import re

from copy import deepcopy

from layout import Ui_MainWindow
from PyQt5.QtWidgets import (
    QMainWindow, QListWidgetItem)
from PyQt5.QtCore import Qt
#

from grammar.grammar import Grammar
from grammar.production import Prod

GRAMMAR_PATTERN = re.compile(r"^[A-Z]'?->[a-z0-9&][A-Z]?(\|[a-z0-9&][A-Z]?)*$")

'''
S -> A B
A -> a A | &
B -> b B | &

S -> A b C D | E F
A -> a A | &
C -> E C F | c
D -> C D | d D d | &
E -> e E | &
F -> F S | f F | g
'''


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setupUi(self)
        self.resize(600, 400)

        self.selected_grammar = None
        self.selected_grammar_name = ''

        self.textEditConsole.setText('Console')

        self.buttonCreateGrammar.clicked.connect(self._create_grammar)

        self.grammarList.currentItemChanged.connect(self._load_grammar)
        self.buttonToPropper.clicked.connect(self._to_proper)

        # buttons
        self.buttonNF.clicked.connect(self._nf)
        self.buttonVI.clicked.connect(self._vi)
        self.buttonNA.clicked.connect(self._na)
        self.buttonNE.clicked.connect(self._ne)

        self.buttonFirst.clicked.connect(self._first)
        self.buttonFirstNT.clicked.connect(self._first_nt)
        self.buttonFollow.clicked.connect(self._follow)

        self.buttonFinite.clicked.connect(self._finite)
        self.buttonEmpty.clicked.connect(self._empty)

        self.buttonCheckRecursion.clicked.connect(self._check_recursion)
        self.buttonFactorSteps.clicked.connect(self._factor)

        self.buttonRemoveDirectRec.clicked.connect(self._remove_direct_recursion)
        self.buttonRemoveIndirectRec.clicked.connect(self._remove_indirect_recursion)

    def _save_grammar(self, name, grammar):
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, grammar)
        self.grammarList.addItem(item)

    def _first(self):
        first = self.selected_grammar.first_sets()
        self.log('First {')
        self.log_dict(first)
        self.log('}')

    def _first_nt(self):
        first_nt = self.selected_grammar.first_NT()
        self.log('First-NT {')
        self.log_dict(first_nt)
        self.log('}')

    def _follow(self):
        follow = self.selected_grammar.follow_sets()
        self.log('Follow {')
        self.log_dict(follow)
        self.log('}')

    def _nf(self):
        nf = self.selected_grammar.productive()
        self.log(f'Productive:\t{nf}')

    def _vi(self):
        grammar = self.selected_grammar
        vi = grammar.reachable(grammar.start)
        self.log(f'Reachable:\t{vi}')

    def _na(self):
        na = self.selected_grammar.simple_table()
        self.log('NA {')
        self.log_dict(na)
        self.log('}')

    def _ne(self):
        ne = self.selected_grammar._epsilon_closure()
        ne = { i[0] for i in ne }
        self.log(f'Epsilon closure:\t{ne}')

    def _empty(self):
        is_empty = self.selected_grammar.is_empty()
        self.log(f'Empty:\t{is_empty}')

    def _finite(self):
        is_finite = self.selected_grammar.is_finite()
        self.log(f'Finite:\t{is_finite}')

    def _factor(self):
        steps = int(self.lineEditFactorSteps.text())

        if steps == 0:
            factored = self.selected_grammar.is_factored()
        else:
            factored = isinstance(self.selected_grammar.factor(steps), Grammar)
        self.log(f'Factor ({steps}):\t{factored}')

    def _remove_direct_recursion(self):
        grammar = deepcopy(self.selected_grammar)
        grammar_name = f'{self.lineInputGrammarName.text()}_direct'

        direct = grammar.has_direct_left_recursion()
        for s in direct:
            grammar.remove_direct_left_recursion(s)

        self.log('Removing direct left recursions')
        self.log_grammar(grammar_name, grammar)
        self._save_grammar(grammar_name, grammar)

    def _check_recursion(self):
        grammar = self.selected_grammar
        direct = grammar.has_direct_left_recursion()
        indirect = grammar.has_indirect_left_recursion()
        self.log(f'Non-terminals with direct recursion:\t{direct}')
        self.log(f'Non-terminals with indirect recursion:\t{indirect}')

    def _remove_indirect_recursion(self):
        grammar = deepcopy(self.selected_grammar)
        grammar_name = f'{self.lineInputGrammarName.text()}_indirect'

        grammar.remove_left_recursion()

        self.log('Removing all left recursions')
        self.log_grammar(grammar_name, grammar)
        self._save_grammar(grammar_name, grammar)


    def _to_proper(self):
        grammar_name = self.selected_grammar_name

        # Create grammars
        epsilon_free = deepcopy(self.selected_grammar)
        epsilon_free.remove_epsilon()
        epsilon_free_name = f'{grammar_name}_epsilon_free'

        simple_free = deepcopy(epsilon_free)
        simple_free.remove_simple()
        simple_free_name = f'{grammar_name}_simple_free'

        unproductive_free = deepcopy(simple_free)
        unproductive_free.remove_unproductive()
        unproductive_free_name = f'{grammar_name}_unproductive_free'

        unreachable_free = deepcopy(unproductive_free)
        unreachable_free.remove_unreachable()
        unreachable_free_name = f'{grammar_name}_unreachable_free'

        # Create list items
        self._save_grammar(epsilon_free_name, epsilon_free)
        self._save_grammar(simple_free_name, simple_free)
        self._save_grammar(unproductive_free_name, unproductive_free)
        self._save_grammar(unreachable_free_name, unreachable_free)

        # Log
        self.log('Intermediary grammars added to list')
        self._nf()
        self._vi()
        self._na()
        self._ne()

    def _create_grammar(self):
        grammar_name = self.lineInputGrammarName.text()
        grammar = self._to_grammar()

        # Log
        self.log('Saving grammar:')
        self.log_grammar(grammar_name, grammar)

        self._save_grammar(grammar_name, grammar)

    def _load_grammar(self, nxt, prev):
        grammar_name = nxt.text()
        grammar = nxt.data(Qt.UserRole)

        self.selected_grammar = grammar
        self.selected_grammar_name = grammar_name

        # Log
        self.log('Loading grammar:')
        self.log_grammar(grammar_name, grammar)

        self.lineInputGrammarName.setText(grammar_name)
        self.textEditGrammarInput.setText(str(grammar))

    def _to_grammar(self):
        grammar_text = self.textEditGrammarInput.toPlainText()
        lines = grammar_text.split('\n')

        terminals = set()
        productions = set()
        non_terminals = set()

        # Start
        start = lines[0].split('->')[0].strip()

        # Non terminals
        for line in lines:
            non_terminal = line.split('->')[0].strip()
            non_terminals.add(non_terminal)

        # Terminals
        for line in lines:
            expressions = line.split('->')[1].split('|')
            for exp in expressions:
                symbols = filter(lambda i: i not in non_terminals, exp.split())
                for symbol in symbols:
                    terminals.add(symbol)

        # Productions
        for line in lines:
            non_terminal = line.split('->')[0].strip()
            expressions = line.split('->')[1].split('|')
            for exp in expressions:
                prod = exp.split()
                new_prod = Prod(non_terminal, tuple(prod))
                productions.add(new_prod)

        return Grammar(non_terminals, terminals, productions, start)

    def log(self, text):
        self.textEditConsole.append(text)

    def log_dict(self, dct):
        for k, v in dct.items():
            self.textEditConsole.append(f'{k}:\t{v}')

    def log_grammar(self, name, grammar):
        self.log(f'Name:\t{name}')
        self.log(f'Start:\t{grammar.start}')
        self.log(f'Vnt:\t{str(grammar.non_terminals)}')
        self.log(f'Vt:\t{str(grammar.terminals)}')
        self.log(f'P:\t{str(grammar.productions)}')
