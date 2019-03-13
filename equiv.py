import re
from itertools import chain


class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


def dictinvert(d):
    inv = {}
    for k, v in d.iteritems():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


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
            if sequent[abs(n - 1)]:
                sequent[abs(n - 1)] += ',' + neg[1:]
            else:
                sequent[abs(n - 1)] += neg[1:]
            to_replace = neg
        else:
            if sequent[abs(n - 1)]:
                sequent[abs(n - 1)] += ',' + neg
            else:
                sequent[abs(n - 1)] += neg
            to_replace = '~(' + neg + ')'

        sequent[n] = sequent[n].replace(to_replace, '')
        sequent[n] = sequent[n].replace(',,', ',')
        if sequent[n]:
            if sequent[n][0] == ',':
                sequent[n] = sequent[n][1:]
            if sequent[n][-1] == ',':
                sequent[n] = sequent[n][:-1]

    return sequent


def negation_remover(sequent, ss):
    sequent = re.split(ss, sequent)
    regex_defs = ['~[A-Za-z]', '~\((\(.*?\))\)', '~\((.*?)\)']
    for rd in regex_defs:
        for n, side in enumerate(sequent):
            negs = re.findall(rd, side)
            sequent = negs_replace(negs, sequent, n)

    return ss.join(sequent)


def seq2rules(sequent, ss, op):
    sequent = re.split(ss, sequent)

    for n, side in enumerate(sequent):
        sequent[n] = re.split(',', side)
    longest_elt = max(chain.from_iterable(sequent), key=len)
    dissolve = re.findall('\((.*?)\)', longest_elt)
    if not dissolve:
        dissolve = re.split(op, longest_elt)

    rule_dict = Dictlist()
    for w1, w2 in zip(dissolve, lang[:len(dissolve)]):
        rule_dict[w1] = w2

    for n, side in enumerate(sequent):
        if n == 0:
            noise = 'Γ'
        else:
            noise = 'Δ'

        for num_elt, elt in enumerate(side):
            if len(rule_dict) > 1:
                side[num_elt] = re.sub(dissolve[0], rule_dict[dissolve[0]][0], elt)
                side[num_elt] = re.sub(dissolve[1], rule_dict[dissolve[1]][0], side[num_elt])
                side[num_elt] = re.sub('\(|\)', '', side[num_elt])
            else:
                while dissolve[0] in side[num_elt]:
                    side[num_elt] = re.sub(dissolve[0], rule_dict[dissolve[0]][0], elt, 1)
                    side[num_elt] = re.sub(dissolve[1], rule_dict[dissolve[1]][1], side[num_elt], 1)

            if not any(ch in side[num_elt] for ch in lang):
                if side[num_elt]:
                    rule_dict[side[num_elt]] = noise
                side[num_elt] = noise

        sequent[n] = ','.join(side)
        if not any(ch in sequent[n] for ch in 'ΓΔ'):
            sequent[n] += ',' + noise
        sequent[n] = sort_formulas(sequent[n], n)

    return sequent, rule_dict


def sort_formulas(side, num_side):
    if num_side == 0:
        sort_ord = {'A': 1, 'B': 2, 'A' + op + 'B': 3, 'Γ': 4}
    else:
        sort_ord = {'Δ': 1, 'A': 2, 'B': 3, 'A' + op + 'B': 4}
    to_sort = re.split(',', side)
    to_sort_num = []
    for elt in to_sort:
        to_sort_num.append(sort_ord[elt])
    to_sort = zip(to_sort_num, to_sort)
    return ','.join([x for _, x in sorted(to_sort)])


def cut(sequent, ss):
    possible_cuts = 'AB'
    sequent_to_cut = sequent.split(ss)
    sequents_after_cut = [ss.join([sequent_to_cut[0], sequent_to_cut[1] + ',~' + possible_cuts[0]]),
                          ss.join(['~' + possible_cuts[0] + ',' + sequent_to_cut[0], sequent_to_cut[1]])]
    solutions = []
    for n in sequents_after_cut:
        n_unsorted = negation_remover(n, ss=ss)
        n_sorted = []
        for num_side, n_side_unsorted in enumerate(re.split(ss, n_unsorted)):
            n_sorted.append(sort_formulas(n_side_unsorted, num_side))
        solutions.append(ss.join(n_sorted))

    return solutions


# '=' is the equivalence for the purpose of a user-friendly input
testSeqs = ['p->p=p',
            '->p=p,p',
            '~p->p=p',
            '->p=p,~p',
            'p=q->p=r,(q=r)=(p=r)',
            'p=q,p=r->(q=r)=(p=r)',
            'p=q->~(p=r),(q=r)=(p=r)',
            'p=q,~(p=r)->(q=r)=(p=r)']
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
lang = 'ABΓΔ'
ss = '⇒'
op = '≡'

# test_seq = testSeqs[0]
# test_seq = '->(p=q)=(q=p)'
test_seq = '->p=p'
test_seq = seq_format(test_seq)
print(test_seq)
seq_step_1 = negation_remover(test_seq, ss=ss)
sequent_signed, rule_dict = seq2rules(seq_step_1, ss=ss, op=op)
print(rule_dict)
sequent_signed = ss.join(sequent_signed)
print('sequent_signed = {}'.format(sequent_signed))
'''try compare and convert, except cut'''
try:
    print('rulesNoise[sequent_signed] = {}'.format(rulesNoise[sequent_signed]))
    for solution in rulesNoise[sequent_signed]:
        print('solution = {}\trules_noise[solution] = {}'.format(solution, rulesNoise[solution]))
except KeyError:
    solutions = cut(sequent_signed, ss)
    print('solutions = {}'.format(solutions))
print('\n')

# TODO: compare sequent with rules and convert to new form
# TODO: save output to tex file
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
