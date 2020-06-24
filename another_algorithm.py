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
    out = [s[:slice_at], s[slice_at+1:]]
    for n, obj in enumerate(out):
        if '(' in obj:
            out[n] = out[n][1:-1]
    return out


def negation_remover(sequent):
    sequent = re.split('⇒', sequent)
    for rd in ['~[A-Za-z]', '~\((\(.*?\))\)', '~\((.*?)\)']:
        for n, side in enumerate(sequent):
            negs = re.findall(rd, side)
            for neg in negs:
                if {neg, '~(' + neg + ')'}.intersection(set([item for side in sequent for item in side.split(',')])):
                    if len(neg) == 2:
                        to_replace = neg
                        neg = neg[1]
                    else:
                        to_replace = '~(' + neg + ')'
                    if sequent[int(not n)]:
                        if neg not in sequent[int(not n)].split(','):
                            sequent[int(not n)] += ',' + neg
                    else:
                        sequent[int(not n)] += neg

                    sequent[n] = sequent[n].replace(to_replace, '')
                    sequent[n] = ','.join(filter(None, re.split(',', sequent[n])))
    return '⇒'.join(sequent)


def check_if_axiom(sequent):
    sequent = re.split('⇒', sequent)
    if set(re.split(',', sequent[0])) & set(re.split(',', sequent[1])):
        return True
    else:
        return False


class Sequent:
    def __init__(self, sequent):
        if '⇒' in sequent:
            self.sequent = sequent
        else:
            self.sequent = seq_format(sequent)
        self.split = re.split('⇒', self.sequent)
        self.single = [set(re.split(',', obj)) for obj in self.split]
        self.sideFlag = None
        self.inv_dict = {ch: '' for ch in 'ABΓΔ'}
        self.base = ''
        self.longest_object = ''

    def update(self, sequent):
        self.sequent = sequent
        self.split = re.split('⇒', self.sequent)
        self.single = [set(re.split(',', obj)) for obj in self.split]

    def unnegate(self):
        self.update(negation_remover(self.sequent))

    def find_longest_object(self):
        longest = str(max([elt for side in self.single for elt in side], key=len))
        self.longest_object = longest
        self.sideFlag = int(longest in self.single[1])


class Prover:
    def __init__(self):
        self.ss = '⇒'
        self.conn = '≡'
        self.tree = nx.DiGraph()
        self.longest_objects = []
        self.rules = {'Γ⇒Δ,A≡B,A,B': 'B,Γ⇒Δ,A≡B,B', # (05) ↑
                      'B,A,Γ⇒Δ,A≡B': 'A,Γ⇒Δ,A,A≡B', # (05) ↓
                      'B,A≡B,Γ⇒Δ,A': 'B,A≡B,Γ⇒Δ,B', # (08) ↑
                      'A,A≡B,Γ⇒Δ,B': 'A,A≡B,Γ⇒Δ,A'} # (08) ↓

    def pipeline(self, seq):
        print(f'current sequent = {seq.sequent}')
        self.tree.add_node(seq.sequent)

        # remove negations
        if '~' in seq.sequent:
            seq.unnegate()
            print('negation removed', seq.sequent)

        # find longest object
        seq.find_longest_object()
        self.longest_objects.append(seq.longest_object)

        # update dict A, B
        seq.inv_dict['A'], seq.inv_dict['B'] = split_by_connective(self.longest_objects[-1], self.conn)

        # update dict G, D
        for ch, n in zip('ΓΔ', [0, 1]):
            seq.inv_dict[ch] = ','.join(set(filter(lambda x: x != self.longest_objects[-1], seq.single[n])))
        print(seq.inv_dict)

        # update base form
        if seq.sideFlag:
            seq.base = 'Γ⇒Δ,A≡B'
        else:
            seq.base = 'A≡B,Γ⇒Δ'

        # perform cut twice (and check if axiom after each cut)
        self.recursive_cut(seq)

    def cut_by(self, sequent, to_cut):
        se = sequent.single
        solutions = [self.ss.join([','.join(obj) for obj in [se[0], se[1].union({sequent.inv_dict[to_cut]})]]),
                     self.ss.join([','.join(obj) for obj in [se[0].union({sequent.inv_dict[to_cut]}), se[1]]])]
        solutions_base = [sequent.base + ',' + to_cut,
                          to_cut + ',' + sequent.base]
        return solutions, solutions_base

    def recursive_cut(self, parent_sequent, possible_cuts='AB', depth=0):
        if possible_cuts:
            print('\t' * depth, end='')
            print(f'Cut (by {possible_cuts[0]} which is {parent_sequent.inv_dict[possible_cuts[0]]})')
            solutions, solutions_base = self.cut_by(parent_sequent, possible_cuts[0])
            depth += 1
            for sol, base in zip(solutions, solutions_base):
                sol = Sequent(sol)
                sol.base = base
                sol.inv_dict = parent_sequent.inv_dict
                self.tree.add_node(sol.sequent)
                self.tree.add_edge(parent_sequent.sequent, sol.sequent)
                if check_if_axiom(sol.sequent):
                    print('\t' * depth, end='')
                    print(f'Solution: {sol.sequent} is an axiom.')
                else:
                    print('\t' * depth, end='')
                    print(f'Solution: {sol.sequent} is NOT an axiom.')
                    self.recursive_cut(sol, possible_cuts[1:], depth)
        else:
            self.from_rules(parent_sequent, depth)

    def from_rules(self, parent_sequent, depth):
        depth += 1
        if parent_sequent.base in self.rules.keys():
            print('\t' * depth, end='')
            print(f'Solution for {parent_sequent.sequent} found in rules.')
            print('\t' * depth, end='')
            print(parent_sequent.base + ' → ' + self.rules[parent_sequent.base])

            out_base = self.rules[parent_sequent.base]
            out_seq = Sequent(multi_replace({**{'A≡B': self.longest_objects[-1]}, **parent_sequent.inv_dict}, out_base))
            out_seq.base = out_base

            self.tree.add_node(out_seq.sequent)
            self.tree.add_edge(parent_sequent.sequent, out_seq.sequent)

            if check_if_axiom(out_seq.sequent):
                print('\t' * depth, end='')
                print(f'Solution: {out_seq.sequent} is an axiom.')
            else:
                print('\t' * depth, end='')
                print('NO JAK TO KURNA NIE.')
        else:
            print('\t' * depth, end='')
            print(f'No solution found for {parent_sequent.sequent}')


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
    prvr = Prover()
    seq_init = Sequent(testseq)
    prvr.pipeline(seq_init)
    print()

# prvr = Prover()
# seq_init = Sequent(testSeqs[6])
# prvr.pipeline(seq_init)
# print()
