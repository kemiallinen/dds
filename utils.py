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
                  '=': '≡'}
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
        sequent[n] = ','.join(filter(None, re.split(',', sequent[n])))

    return sequent


def sort_formulas(side, num_side, op):
    if op == '≡':
        side = side.replace('B≡A', 'A≡B')
    if num_side == 0:
        sort_ord = {'A': 1, 'B': 2, 'A' + op + 'B': 3, 'Γ': 4}
    else:
        sort_ord = {'Δ': 1, 'A': 2, 'B': 3, 'A' + op + 'B': 4, 'B' + op + 'A': 5}
    to_sort = re.split(',', side)
    to_sort_num = []
    for elt in to_sort:
        to_sort_num.append(sort_ord[elt])
    to_sort = zip(to_sort_num, to_sort)
    return ','.join([x for _, x in sorted(to_sort)])
