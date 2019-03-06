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


def negation_remover(sequent):
    negated_elt = re.findall('~(.*?)[⇒,]', sequent)
    re.findall('~\((.*?)[\)⇒,]', 'p≡q⇒~(p≡r),~(q≡r)≡(p≡r),~p')


def seq_split(sequent):
    sequent = re.split('⇒', sequent)
    formulas = []
    later_append = []

    # for i, f in enumerate(sequent):
    #     temp = []
    #     for g in re.split(',', f):
    #         if len(g) > 6:
    #             g = re.findall('\((.*?)\)', g)
    #         temp.append(g)
    #     if temp:
    #         for k, t in enumerate(temp):
    #             if t:
    #                 if t[0] == '~':
    #                     g = re.findall('\((.*?)\)', t)
    #                     if not g:
    #                         g = t[1:]
    #                     if i == 0:
    #                         later_append = g
    #                     else:
    #                         formulas[0].append(g[0])  # TODO: manage empty lists during nr process
    #                     temp.remove(t)
    #                     print('temp = {}'.format(temp))
    #                     print('len temp = {}'.format(len(temp)))
    #     if i == 1:
    #         if later_append:
    #             temp.append(later_append[0])
    #     formulas.append(temp)
    # print(str(formulas[0]))
    # print(str(formulas[1]))
    # if len(formulas[0]) and len(formulas[1]):
    #     formulas_txt = formulas[0][0] + '⇒' + formulas[1][0]
    # elif len(formulas[0]) == 0:
    #     formulas_txt = '⇒' + formulas[1][0]
    # else:
    #     formulas_txt = formulas[0][0] + '⇒'
    return formulas_txt


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

print('single[2][0][0] = {}'.format(singleFormulas[1][0][0]))
print('len single[2][0][0] = {}'.format(len(singleFormulas[1][0][0])))
