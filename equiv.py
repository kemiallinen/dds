import re

# @ is equivalence
testSeqs = ['p->p@p',
            '->p@p,p',
            '~p->p@p',
            '->p@p,~p',
            'p@q->p@r,(q@r)@(p@r)',
            'p@q,p@r->(q@r)@(p@r)',
            'p@q->~(p@r),(q@r)@(p@r)',
            'p@q,~(p@r)->(q@r)@(p@r)']

rulesNoise = {'B,A@B,G→D':      ['A,B,G→D',
                                 'A,A@B,G→D'],
              'G→D,A,A@B':      ['B,G→D,A@B',
                                 'B,G→D,A'],
              'G→D,B,A@B':      'A,G→D,A@B',
              'B,G→D,A@B':      'B,G→D,A',
              'A,G→D,A@B':      'A,G→D,B',
              'A,G→D,B':        'G→D,B,A@B',
              'A@B,G→D,A':      ['A@B,G→D,B',
                                 'G→D,A,B'],
              'A,A@B,G→D':      'A,B,G→D',
              'A@B,G→D,B':      'G→D,A,B',
              'A,B,G→D,A@B':    ['A,A@B,G→D,B',
                                 'B,A@B,G→D,A'],
              'B,A@B,G→D,A':    'G→D,A,B,A@B',
              'A,A@B,G→D,B':    ['G→D,A,B,A@B',
                                 'B,A@B,G→D,A'],
              'G→D,A,B,A@B':    'A,B,G→D,A@B'}

testSeqsFormatted = []

for seq in testSeqs:
    testSeqsFormatted.append(re.sub('->', '→', seq))

print(testSeqsFormatted)

testSeqsSplitted = []

for seq in testSeqsFormatted:
    testSeqsSplitted.append(re.split('→', seq))

print(testSeqsSplitted)

singleFormulas = []

