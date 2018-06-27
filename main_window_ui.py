import re

from copy import deepcopy
from functools import wraps
from pprint import pprint

from layout import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem
from PyQt5.QtCore import Qt

from grammar.grammar import Grammar
from grammar.production import Prod

SPACE_REMOVE_RE = re.compile(r' +')
NON_TERMINAL_RE = re.compile(r'[A-Z][\d]*')
TERMINAL_RE = re.compile(r'[a-z\d]+')

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

    def check_name(fun):
        @wraps(fun)
        def wrapped(self, *args, **kwargs):
            if self.lineInputGrammarName.text() == '':
                self.log('There is no name for grammar')
                return
            return fun(self)
        return wrapped

    def check_factor(fun):
        @wraps(fun)
        def wrapped(self, *args, **kwargs):
            num = self.lineEditFactorSteps.text().strip()
            try:
                num = int(num)
                assert num >= 0
            except Exception as e:
                self.log('Steps is not a positive number')
                return
            return fun(self)
        return wrapped

    def has_grammar(fun):
        @wraps(fun)
        def wrapped(self, *args, **kwargs):
            if self.selected_grammar == None:
                self.log('No grammar selected')
                return
            return fun(self)
        return wrapped

    def check_grammar(fun):
        @wraps(fun)
        def wrapped(self, *args, **kwargs):
            text = self.textEditGrammarInput.toPlainText()
            table = self._filter_input(text)

            # Check non-terminals
            for non_terminal in table.keys():
                if not NON_TERMINAL_RE.match(non_terminal):
                    self.log(f'Invalid non-terminal: {non_terminal}')
                    return

            # Check productions
            for expressions in table.values():
                for exp in expressions:
                    print(exp)
                    if exp == Grammar.EPSILON:
                        continue
                    for symbol in exp.split():
                        if not self._valid_symbol(symbol):
                            self.log(f'Invalid expression: {exp}')
                            return

            return fun(self)
        return wrapped

    def _valid_symbol(self, symbol):
        return re.match(NON_TERMINAL_RE, symbol) or re.match(TERMINAL_RE, symbol)

    def _filter_input(self, input_str):
        lines = input_str.split('\n')

        # Filter empty lines
        for line in list(lines):
            if line == '':
                lines.remove(line)

        table = {}

        # Get non-terminals
        for line in lines:
            line = re.sub(SPACE_REMOVE_RE, ' ', line).strip()
            non_terminal = line.split('->')[0].strip()
            expressions = line.split('->')[1].split('|')
            table[non_terminal] = expressions

        pprint(table)

        return table

    def _save_grammar(self, name, grammar):
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, grammar)
        self.grammarList.addItem(item)

    @has_grammar
    def _first(self):
        first = self.selected_grammar.first_sets()
        self.log('First {')
        self.log_dict(first)
        self.log('}')

    @has_grammar
    def _first_nt(self):
        first_nt = self.selected_grammar.first_NT()
        self.log('First-NT {')
        self.log_dict(first_nt)
        self.log('}')

    @has_grammar
    def _follow(self):
        follow = self.selected_grammar.follow_sets()
        self.log('Follow {')
        self.log_dict(follow)
        self.log('}')

    @has_grammar
    def _nf(self):
        nf = self.selected_grammar.productive()
        self.log(f'Productive:\t{nf}')

    @has_grammar
    def _vi(self):
        grammar = self.selected_grammar
        vi = grammar.reachable(grammar.start)
        self.log(f'Reachable:\t{vi}')

    @has_grammar
    def _na(self):
        na = self.selected_grammar.simple_table()
        self.log('NA {')
        self.log_dict(na)
        self.log('}')

    @has_grammar
    def _ne(self):
        ne = self.selected_grammar._epsilon_closure()
        ne = { i[0] for i in ne }
        self.log(f'Epsilon closure:\t{ne}')

    @has_grammar
    def _empty(self):
        is_empty = self.selected_grammar.is_empty()
        self.log(f'Empty:\t{is_empty}')

    @has_grammar
    def _finite(self):
        is_finite = self.selected_grammar.is_finite()
        self.log(f'Finite:\t{is_finite}')

    @has_grammar
    @check_factor
    def _factor(self):
        steps = int(self.lineEditFactorSteps.text().strip())

        if steps == 0:
            factored = self.selected_grammar.is_factored()
        else:
            factored = isinstance(self.selected_grammar.factor(steps), Grammar)
        self.log(f'Factor ({steps}):\t{factored}')

    @has_grammar
    def _remove_direct_recursion(self):
        grammar = deepcopy(self.selected_grammar)
        grammar_name = f'{self.lineInputGrammarName.text()}_direct'

        direct = grammar.has_direct_left_recursion()
        for s in direct:
            grammar.remove_direct_left_recursion(s)

        self.log('Removing direct left recursions')
        self.log_grammar(grammar_name, grammar)
        self._save_grammar(grammar_name, grammar)

    @has_grammar
    def _check_recursion(self):
        grammar = self.selected_grammar
        direct = grammar.has_direct_left_recursion()
        indirect = grammar.has_indirect_left_recursion()
        self.log(f'Non-terminals with direct recursion:\t{direct}')
        self.log(f'Non-terminals with indirect recursion:\t{indirect}')

    @has_grammar
    def _remove_indirect_recursion(self):
        grammar = deepcopy(self.selected_grammar)
        grammar_name = f'{self.lineInputGrammarName.text()}_indirect'

        grammar.remove_left_recursion()

        self.log('Removing all left recursions')
        self.log_grammar(grammar_name, grammar)
        self._save_grammar(grammar_name, grammar)

    @has_grammar
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

    @check_name
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

    @check_grammar
    def _to_grammar(self):
        grammar_text = self.textEditGrammarInput.toPlainText()
        table = self._filter_input(grammar_text)

        terminals = set()
        productions = set()
        non_terminals = set(table.keys())

        # Start
        start = grammar_text.split('\n')[0].split('->')[0].strip()

        # Terminals
        for expression in table.values():
            for symbol in expression:
                if symbol == Grammar.EPSILON:
                    continue

                if symbol not in non_terminals:
                    terminals.add(symbol)

        # Productions
        for nt, prods in table.items():
            for exp in prods:
                productions.add(Prod(nt, tuple(exp)))

        return Grammar(non_terminals, terminals, productions, start)

    def log(self, text):
        self.textEditConsole.append(text)

    def log_dict(self, dct):
        for k, v in dct.items():
            self.textEditConsole.append(f'{k}:\t{v}')

    def log_grammar(self, name, grammar):
        self.log(f'Name:\t{name}')
        self.log(f'Vnt:\t{str(grammar.non_terminals)}')
        self.log(f'Vt:\t{str(grammar.terminals)}')
        self.log(str(grammar))
