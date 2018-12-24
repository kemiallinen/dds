import re


def multi_replace(dictionary, text):
    """
    http://code.activestate.com/recipes/81330-single-pass-multiple-replace/
    :param dictionary:  dict of keys to be replaced by respective values
    :param text:        input string on which we perform replacement
    :return:            string with replaced values
    """
    regex = re.compile('(%s)' % '|'.join(map(re.escape, dictionary.keys())))
    return regex.sub(lambda mo: dictionary[mo.string[mo.start():mo.end()]], text)


def seq_format(sequent):
    dictionary = {'->': '⇒',
                  '=':  '≡'}
    return multi_replace(dictionary, sequent)


def seq_split(sequent):
    sequent = re.split('⇒', sequent)
    formulas = []
    for f in sequent:
        temp = []
        for g in re.split(',', f):
            if len(g) > 6:
                g = re.findall('\((.*?)\)', g)
            temp.append(g)
        formulas.append(temp)
    return formulas


def purge_negations(sequent):
    seq_temp = [item for slist in sequent for item in slist]
    for i, f in enumerate(seq_temp):
        if f:
            if f[0] == '~':
                g = re.findall('\((.*?)\)', f)
                if not g:
                    g = f[1:]
                if i < len(sequent[0]):
                    sequent[1].append(g)
                else:
                    sequent[0].append(g)    #TODO: purge negated formula
    return sequent

    print('sequent={}'.format(sequent))
    print('len(sequent)={}'.format(len(sequent)))
    print('len(sequent)[0]={}'.format(len(sequent[0])))
    print('len(sequent)[1]={}'.format(len(sequent[1])))
    print('seq_temp={}'.format(seq_temp))
    print('len(seq_temp)={}'.format(len(seq_temp)))

    return []
# TODO: negation remover

# TODO: seq2rules

# TODO: save output to tex file

# '=' is the equivalence for the purpose of a user-friendly input
testSeqs = ['p->p=p',
            '->p=p,p',
            '~p->p=p',
            '->p=p,~p',
            'p=q->p=r,(q=r)=(p=r)',
            'p=q,p=r->(q=r)=(p=r)',
            'p=q->~(p=r),(q=r)=(p=r)',
            'p=q,~(p=r)->(q=r)=(p=r)']

[print('testSeqs[{}] = {}'.format(i, seq)) for i, seq in enumerate(testSeqs)]
print('\n')

rulesNoise = {'B,A≡B,G⇒D':      ['A,B,G⇒D',
                                 'A,A≡B,G⇒D'],
              'G⇒D,A,A≡B':      ['B,G⇒D,A≡B',
                                 'B,G⇒D,A'],
              'G⇒D,B,A≡B':      ['A,G⇒D,A≡B',
                                 'A,G⇒D,B'],
              'B,G⇒D,A≡B':      ['B,G⇒D,A',
                                 'G⇒D,A,A≡B'],
              'A,G⇒D,A≡B':      ['A,G⇒D,B',
                                 'G⇒D,B,A≡B'],
              'A,G⇒D,B':        ['G⇒D,B,A≡B',
                                 'A,G⇒D,A≡B'],
              'A≡B,G⇒D,A':      ['A≡B,G⇒D,B',
                                 'G⇒D,A,B'],
              'A,A≡B,G⇒D':      ['A,B,G⇒D',
                                 'B,A≡B,G⇒D'],
              'A≡B,G⇒D,B':      ['G⇒D,A,B',
                                 'A≡B,G⇒D,A'],
              'A,B,G⇒D,A≡B':    ['A,A≡B,G⇒D,B',
                                 'B,A≡B,G⇒D,A',
                                 'G⇒D,A,B,A≡B'],
              'B,A≡B,G⇒D,A':    ['G⇒D,A,B,A≡B',
                                 'A,B,G⇒D,A≡B'],
              'A,A≡B,G⇒D,B':    ['G⇒D,A,B,A≡B',
                                 'B,A≡B,G⇒D,A',
                                 'A,B,G⇒D,A≡B'],
              'G⇒D,A,B,A≡B':    ['A,B,G⇒D,A≡B',
                                 'B,A≡B,G⇒D,A'],
              'A,B,G⇒D':        'B,A≡B,G⇒D',
              'B,G⇒D,A':        ['G⇒D,A,A≡B',
                                 'B,G⇒D,A≡B'],
              'G⇒D,A,B':        'A≡B,G⇒D,B'}

rulesNoiseOneSided = {'B,A≡B,G⇒D':      ['A,B,G⇒D',
                                 'A,A≡B,G⇒D'],
              'G⇒D,A,A≡B':      ['B,G⇒D,A≡B',
                                 'B,G⇒D,A'],
              'G⇒D,B,A≡B':      'A,G⇒D,A≡B',
              'B,G⇒D,A≡B':      'B,G⇒D,A',
              'A,G⇒D,A≡B':      'A,G⇒D,B',
              'A,G⇒D,B':        'G⇒D,B,A≡B',
              'A≡B,G⇒D,A':      ['A≡B,G⇒D,B',
                                 'G⇒D,A,B'],
              'A,A≡B,G⇒D':      'A,B,G⇒D',
              'A≡B,G⇒D,B':      'G⇒D,A,B',
              'A,B,G⇒D,A≡B':    ['A,A≡B,G⇒D,B',
                                 'B,A≡B,G⇒D,A'],
              'B,A≡B,G⇒D,A':    'G⇒D,A,B,A≡B',
              'A,A≡B,G⇒D,B':    ['G⇒D,A,B,A≡B',
                                 'B,A≡B,G⇒D,A'],
              'G⇒D,A,B,A≡B':    'A,B,G⇒D,A≡B'}

testSeqsFormatted = []

[testSeqsFormatted.append(seq_format(seq)) for seq in testSeqs]

[print('testSeqsFormatted[{}] = {}'.format(i, seq)) for i, seq in enumerate(testSeqsFormatted)]
print('\n')

singleFormulas = []

[singleFormulas.append(seq_split(seq)) for seq in testSeqsFormatted]

[print('singleFormulas[{}] = {}'.format(i, sinFor)) for i, sinFor in enumerate(singleFormulas)]
