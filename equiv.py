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


def negs_replace(negs, sequent, n):
    for neg in negs:
        if len(neg) == 2:
            sequent[abs(n - 1)] += ',' + neg[1:]
            to_replace = neg
        else:
            sequent[abs(n - 1)] += ',' + neg
            to_replace = '~(' + neg + ')'
        sequent[n] = sequent[n].replace(to_replace, '')
        sequent[n] = sequent[n].replace(',,', ',')
        if sequent[n][0] == ',':
            sequent[n] = sequent[n][1:]
    return sequent


def negation_remover(sequent, op):
    sequent = re.split(op, sequent)
    regex_defs = ['~[A-Za-z]', '~\((\(.*?\))\)', '~\((.*?)\)']
    for rd in regex_defs:
        for n, elt in enumerate(sequent):
            negs = re.findall(rd, elt)
            sequent = negs_replace(negs, sequent, n)
            print(sequent)
    return op.join(sequent)


test_seq = '~p,~q,~(p≡r)⇒~((q≡r)≡(p≡r)),~p'
print(test_seq)
print(negation_remover(test_seq, op='⇒'))

# # TODO: seq2rules
#
# # TODO: save output to tex file
#
# # '=' is the equivalence for the purpose of a user-friendly input
# testSeqs = ['p->p=p',
#             '->p=p,p',
#             '~p->p=p',
#             '->p=p,~p',
#             'p=q->p=r,(q=r)=(p=r)',
#             'p=q,p=r->(q=r)=(p=r)',
#             'p=q->~(p=r),(q=r)=(p=r)',
#             'p=q,~(p=r)->(q=r)=(p=r)']
#
# [print('testSeqs[{}] = {}'.format(i, seq)) for i, seq in enumerate(testSeqs)]
# print('\n')
#
# rulesNoise = {'B,A≡B,G⇒D':      ['A,B,G⇒D',
#                                  'A,A≡B,G⇒D'],
#               'G⇒D,A,A≡B':      ['B,G⇒D,A≡B',
#                                  'B,G⇒D,A'],
#               'G⇒D,B,A≡B':      ['A,G⇒D,A≡B',
#                                  'A,G⇒D,B'],
#               'B,G⇒D,A≡B':      ['B,G⇒D,A',
#                                  'G⇒D,A,A≡B'],
#               'A,G⇒D,A≡B':      ['A,G⇒D,B',
#                                  'G⇒D,B,A≡B'],
#               'A,G⇒D,B':        ['G⇒D,B,A≡B',
#                                  'A,G⇒D,A≡B'],
#               'A≡B,G⇒D,A':      ['A≡B,G⇒D,B',
#                                  'G⇒D,A,B'],
#               'A,A≡B,G⇒D':      ['A,B,G⇒D',
#                                  'B,A≡B,G⇒D'],
#               'A≡B,G⇒D,B':      ['G⇒D,A,B',
#                                  'A≡B,G⇒D,A'],
#               'A,B,G⇒D,A≡B':    ['A,A≡B,G⇒D,B',
#                                  'B,A≡B,G⇒D,A',
#                                  'G⇒D,A,B,A≡B'],
#               'B,A≡B,G⇒D,A':    ['G⇒D,A,B,A≡B',
#                                  'A,B,G⇒D,A≡B'],
#               'A,A≡B,G⇒D,B':    ['G⇒D,A,B,A≡B',
#                                  'B,A≡B,G⇒D,A',
#                                  'A,B,G⇒D,A≡B'],
#               'G⇒D,A,B,A≡B':    ['A,B,G⇒D,A≡B',
#                                  'B,A≡B,G⇒D,A'],
#               'A,B,G⇒D':        'B,A≡B,G⇒D',
#               'B,G⇒D,A':        ['G⇒D,A,A≡B',
#                                  'B,G⇒D,A≡B'],
#               'G⇒D,A,B':        'A≡B,G⇒D,B'}
#
# rulesNoiseOneSided = {'B,A≡B,G⇒D':      ['A,B,G⇒D',
#                                  'A,A≡B,G⇒D'],
#               'G⇒D,A,A≡B':      ['B,G⇒D,A≡B',
#                                  'B,G⇒D,A'],
#               'G⇒D,B,A≡B':      'A,G⇒D,A≡B',
#               'B,G⇒D,A≡B':      'B,G⇒D,A',
#               'A,G⇒D,A≡B':      'A,G⇒D,B',
#               'A,G⇒D,B':        'G⇒D,B,A≡B',
#               'A≡B,G⇒D,A':      ['A≡B,G⇒D,B',
#                                  'G⇒D,A,B'],
#               'A,A≡B,G⇒D':      'A,B,G⇒D',
#               'A≡B,G⇒D,B':      'G⇒D,A,B',
#               'A,B,G⇒D,A≡B':    ['A,A≡B,G⇒D,B',
#                                  'B,A≡B,G⇒D,A'],
#               'B,A≡B,G⇒D,A':    'G⇒D,A,B,A≡B',
#               'A,A≡B,G⇒D,B':    ['G⇒D,A,B,A≡B',
#                                  'B,A≡B,G⇒D,A'],
#               'G⇒D,A,B,A≡B':    'A,B,G⇒D,A≡B'}
#
# testSeqsFormatted = []
#
# [testSeqsFormatted.append(seq_format(seq)) for seq in testSeqs]
#
# [print('testSeqsFormatted[{}] = {}'.format(i, seq)) for i, seq in enumerate(testSeqsFormatted)]
# print('\n')
#
# singleFormulas = []
#
# [singleFormulas.append(seq_split(seq)) for seq in testSeqsFormatted]
#
# [print('singleFormulas[{}] = {}'.format(i, sinFor)) for i, sinFor in enumerate(singleFormulas)]
#
# print('single[2][0][0] = {}'.format(singleFormulas[1][0][0]))
# print('len single[2][0][0] = {}'.format(len(singleFormulas[1][0][0])))
