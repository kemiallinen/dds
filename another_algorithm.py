import re
import networkx as nx


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


class Prover:
    def __init__(self, sequent):
        self.sequent = seq_format(sequent)
        self.ss = '⇒'
        self.conn = '≡'
        self.lang = 'ABΓΔ'
        self.sideFlag = None
        self.inv_dict = {ch: '' for ch in self.lang}
        self.tree = nx.DiGraph()
        self.tree.add_node(self.sequent)
        self.longest_objects = []

    def pipeline(self, cut=True, actual_parent=None):
        print(self.sequent)

        # find longest object
        seq_spl = re.split(self.ss, self.sequent)
        single_elts = [side.split(',') for side in seq_spl]
        self.longest_objects.append(self.find_longest_object(single_elts))
        print(self.longest_objects[-1])

        # update dict A, B
        self.inv_dict['A'], self.inv_dict['B'] = split_by_connective(self.longest_objects[-1], self.conn)
        print(self.inv_dict)

        # update dict G, D
        self.inv_dict['Γ'] = list(filter(lambda x: x != self.longest_objects[-1], single_elts[0]))
        self.inv_dict['Δ'] = list(filter(lambda x: x != self.longest_objects[-1], single_elts[1]))
        print(self.inv_dict)

        # perform cut twice (and check if axiom after each cut)
        actual_parent = self.sequent
        solutions = [self.sequent + ',' + self.inv_dict['A'],
                     self.inv_dict['A'] + ',' + self.sequent]
        print(solutions)
        # parentheses...
        # recurrently call pipeline() for each solution
        solutions = []
        for solution in solutions:
            if self.conn in solution:
                self.pipeline()

    def find_longest_object(self, elts):
        elts_flatten = [elt for side in elts for elt in side]
        longest = str(max(elts_flatten, key=len))
        if longest in elts[0]:
            self.sideFlag = 0
        else:
            self.sideFlag = 1
        return longest

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
    prvr = Prover(testseq)
    prvr.pipeline()
    print()
