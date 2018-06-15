from collections import namedtuple

'''
Simple named tuple class to be used as productions in this implementation.

Attributes:
    n: Non-terminal symbol of production
    p: Production from the n symbol.
'''
Prod = namedtuple('Prod', [ 'n', 'p' ])
