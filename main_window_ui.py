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

    def _to_proper(self):
        grammar_name = self.selected_grammar_name

        # Create grammars
        epsilon_free = deepcopy(self.selected_grammar)
        ne = epsilon_free._epsilon_closure().copy()
        epsilon_free.remove_epsilon()
        epsilon_free_name = f'{grammar_name}_epsilon_free'

        simple_free = deepcopy(epsilon_free)
        na = deepcopy(simple_free.simple_table())
        simple_free.remove_simple()
        simple_free_name = f'{grammar_name}_simple_free'

        useless_free = deepcopy(simple_free)
        vi = useless_free.reachable(useless_free.start).copy()
        nf = useless_free.productive().copy()
        useless_free.remove_useless()
        useless_free_name = f'{grammar_name}_useless_free'

        # Create list items
        item_epsilon = QListWidgetItem(epsilon_free_name)
        item_epsilon.setData(Qt.UserRole, epsilon_free)
        item_simple = QListWidgetItem(simple_free_name)
        item_simple.setData(Qt.UserRole, simple_free)
        item_useless = QListWidgetItem(useless_free_name)
        item_useless.setData(Qt.UserRole, useless_free)

        # Add to list
        self.grammarList.addItem(item_epsilon)
        self.grammarList.addItem(item_simple)
        self.grammarList.addItem(item_useless)

        # Log
        self.log('Intermediary grammars added to list')
        self.log(f'Nf:\t{nf}')
        self.log(f'Vi:\t{vi}')
        self.log(f'Na:\t{na}')
        self.log(f'Ne:\t{ne}')


    def _create_grammar(self):
        grammar_name = self.lineInputGrammarName.text()
        grammar = self._to_grammar()

        # Log
        self.log('Saving grammar:')
        self.log_grammar(grammar_name, grammar)

        item = QListWidgetItem(grammar_name)
        item.setData(Qt.UserRole, grammar)

        self.grammarList.addItem(item)

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

    def log_grammar(self, name, grammar):
        self.log(f'Name:\t{name}')
        self.log(f'Start:\t{grammar.start}')
        self.log(f'Vnt:\t{str(grammar.non_terminals)}')
        self.log(f'Vt:\t{str(grammar.terminals)}')
        self.log(f'P:\t{str(grammar.productions)}')
