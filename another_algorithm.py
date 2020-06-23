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


def split_by_connective(s, conn):
    """
    Well, that's obviously an overkill function, BUT - it's ready for non-trivial cases like "p o (p o q)", where one
    can't simply split string in half. Maybe someday I'll thank myself for this one.
    :param s: logical object to be split (str)
    :param conn: connective (str)
    :return: object split by the main connective (list of strings)
    """
    from itertools import accumulate
    # create a list representing "parentheses depth"
    # e.g.: s = '(poq)o(qor)', par_nest=[1,1,1,1,0,0,1,1,1,1,0]
    par_nest = list(accumulate((ch == "(") - (ch == ")") for ch in s))
    # look for indices under which we can find connective at the minimum value of parentheses depth
    slice_at = [i for i, ch in enumerate(s) if (ch == conn) and (par_nest[i] == min(par_nest))][0]
    return [s[:slice_at], s[slice_at+1:]]


class aaProver:
    def __init__(self, sequent):
        self.sequent = seq_format(sequent)
        self.ss = '⇒'
        self.conn = '≡'
        self.lang = 'ABΓΔ'

    def pipeline(self):
        # TODO: find connective + on which side?
        print(self.sequent)
        longest_object = self.find_longest_object()
        print(longest_object)
        print(split_by_connective(longest_object, self.conn))

    def find_longest_object(self):
        sequent = re.split(self.ss, self.sequent)
        elts = [elt for side in sequent for elt in side.split(',')]
        return str(max(elts, key=len))


# TODO: assign objects to A, B and noise
# TODO: perform cut twice (and check if axiom after each cut - fast base2seq?)


testSeqs = ['->p=p',
            'p->p=p',
            '->p=p,p',
            '~p->p=p',
            '->p=p,~p',
            '->(p=q)=(q=p)',
            'p=q->p=r,(q=r)=(p=r)',
            'p=q,p=r->(q=r)=(p=r)',
            'p=q->~(p=r),(q=r)=(p=r)',
            'p=q,~(p=r)->(q=r)=(p=r)']
for testseq in testSeqs:
    prvr = aaProver(testseq)
    prvr.pipeline()
    print()
