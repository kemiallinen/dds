import re
import pandas as pd
from copy import deepcopy


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


def check_if_tautology(prover, verbose=True):
    parents = prover.tree['parent'].to_numpy()[1:]
    values = prover.tree['value'].to_numpy()[1:]
    val_par_diff = set(values).difference(set(parents))
    if_leaves_are_axioms = [check_if_axiom(x) for x in val_par_diff]
    if verbose:
        for seq, state in zip(val_par_diff, if_leaves_are_axioms):
            print(f'{state}\t\t{seq}')
        print()
    return all(if_leaves_are_axioms)


class Sequent:
    def __init__(self, sequent, banned=None):
        if '⇒' in sequent:
            self.sequent = sequent
        else:
            self.sequent = seq_format(sequent)
        if banned is None:
            self.banned = set()
        else:
            self.banned = banned
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
        unn_seq = negation_remover(self.sequent)
        self.update(unn_seq)

    def find_longest_object(self):
        try:
            longest = str(max({elt for side in self.single for elt in side}.difference(self.banned), key=len))
            self.sideFlag = int(longest in self.single[1])
        except ValueError:
            longest = ''
            self.sideFlag = -1
        self.longest_object = longest
        self.banned.add(longest)


class Prover:
    def __init__(self):
        self.ss = '⇒'
        self.conn = '≡'
        self.tree = pd.DataFrame(columns=['depth', 'parent', 'value', 'operation'])
        self.rules = {'Γ⇒Δ,A≡B,A,B': ['B,Γ⇒Δ,A≡B,B', '(05) ↑'],
                      'B,A,Γ⇒Δ,A≡B': ['A,Γ⇒Δ,A,A≡B', '(05) ↓'],
                      'B,A≡B,Γ⇒Δ,A': ['B,A≡B,Γ⇒Δ,B', '(08) ↑'],
                      'A,A≡B,Γ⇒Δ,B': ['A,A≡B,Γ⇒Δ,A', '(08) ↓']}

    def pipeline(self, seq, depth=0):
        # print(f'depth = {depth} // current sequent = {seq.sequent}')
        # self.tree.add_node(seq.sequent)
        if self.tree.empty:
            self.tree = self.tree.append({'depth': depth,
                                          'parent': 'ROOT',
                                          'value': seq.sequent,
                                          'operation': 'START'},
                                         ignore_index=True)

        # remove negations
        if '~' in seq.sequent:
            seq.unnegate()
            print('negation removed', seq.sequent)

        # find longest object
        seq.find_longest_object()

        if self.conn in seq.longest_object:

            # print(f'depth = {depth}')
            # print(seq.banned)

            # update dict A, B
            seq.inv_dict['A'], seq.inv_dict['B'] = split_by_connective(seq.longest_object, self.conn)

            # update dict G, D
            for ch, n in zip('ΓΔ', [0, 1]):
                seq.inv_dict[ch] = ','.join(set(filter(lambda x: x != seq.longest_object, seq.single[n])))
            # print(seq.inv_dict)

            # update base form
            if seq.sideFlag:
                seq.base = 'Γ⇒Δ,A≡B'
            else:
                seq.base = 'A≡B,Γ⇒Δ'

            # perform cut twice (and check if axiom after each cut)
            self.recursive_cut(seq, depth=depth)

        else:
            pass
            # print('******** NA ********')

    def cut_by(self, sequent, to_cut):
        se = sequent.single
        solutions = [self.ss.join([','.join(obj) for obj in [se[0], se[1].union({sequent.inv_dict[to_cut]})]]),
                     self.ss.join([','.join(obj) for obj in [se[0].union({sequent.inv_dict[to_cut]}), se[1]]])]
        solutions_base = [sequent.base + ',' + to_cut,
                          to_cut + ',' + sequent.base]
        return solutions, solutions_base

    def recursive_cut(self, parent_sequent, possible_cuts='AB', depth=0):
        if possible_cuts:
            # print('*'*30)
            # print('\t' * depth, end='')
            # print(f'parent_seq = {parent_sequent.sequent}, id = {id(parent_sequent)}')
            # print('\t' * depth, end='')
            # print(f'banned = {parent_sequent.banned}')
            # print('\t' * depth, end='')
            # print(f'inv_dict = {parent_sequent.inv_dict}')
            # print('*'*30)
            #
            # print('\t' * depth, end='')
            # print(f'Cut (by {possible_cuts[0]} which is {parent_sequent.inv_dict[possible_cuts[0]]})')
            solutions, solutions_base = self.cut_by(parent_sequent, possible_cuts[0])
            depth += 1
            for sol, base in zip(solutions, solutions_base):
                sol = Sequent(sol, banned=parent_sequent.banned)
                sol.base = base
                sol.inv_dict = parent_sequent.inv_dict
                # self.tree.add_node(sol.sequent)
                # self.tree.add_edge(parent_sequent.sequent, sol.sequent)
                self.tree = self.tree.append({'depth': depth,
                                              'parent': parent_sequent.sequent,
                                              'value': sol.sequent,
                                              'operation': f'CUT by {possible_cuts[0]} / {parent_sequent.inv_dict[possible_cuts[0]]}'},
                                             ignore_index=True)
                if check_if_axiom(sol.sequent):
                    pass
                    # print('\t' * depth, end='')
                    # print(f'Solution: {sol.sequent} is an axiom.')
                else:
                    # print('\t' * depth, end='')
                    # print(f'Solution: {sol.sequent} is NOT an axiom.')
                    self.recursive_cut(sol, possible_cuts[1:], depth=depth)
        else:
            self.from_rules(parent_sequent, depth=depth)

    def from_rules(self, parent_sequent, depth=0):
        if parent_sequent.base in self.rules.keys():
            depth += 1
            # print('\t' * depth, end='')
            # print(f'Solution for {parent_sequent.sequent} found in rules.')
            # print('\t' * depth, end='')
            # print(parent_sequent.base + ' → ' + self.rules[parent_sequent.base][0])

            out_base = self.rules[parent_sequent.base][0]
            out_seq = Sequent(multi_replace({**{'A≡B': parent_sequent.longest_object}, **parent_sequent.inv_dict}, out_base),
                              banned=parent_sequent.banned)
            out_seq.base = out_base

            # self.tree.add_node(out_seq.sequent)
            # self.tree.add_edge(parent_sequent.sequent, out_seq.sequent)
            self.tree = self.tree.append({'depth': depth,
                                          'parent': parent_sequent.sequent,
                                          'value': out_seq.sequent,
                                          'operation': self.rules[parent_sequent.base][1]},
                                         ignore_index=True)

            # if check_if_axiom(out_seq.sequent):
                # print('\t' * depth, end='')
                # print(f'Solution: {out_seq.sequent} is an axiom.')
            # else:
                # print('\t' * depth, end='')
                # print('NO JAK TO KURNA NIE.')
        else:
            # print('\t' * depth, end='')
            # print(f'No solution found for {parent_sequent.sequent}')
            # print('*'*20)
            self.pipeline(deepcopy(parent_sequent), depth=depth)


pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)
testSeqs = ['->p=p',
            'p->p=p',
            '->p=p,p',
            '~p->p=p',
            '->p=p,~p',
            '->(p=q)=(q=p)',
            'p=q->p=r,(q=r)=(p=r)',
            'p=q,p=r->(q=r)=(p=r)',
            'p=q->~(p=r),(q=r)=(p=r)',
            'p=q,~(p=r)->(q=r)=(p=r)',
            '(p=r)=(q=s)->(p=q)=(r=s)',
            'p=r->(p=q)=(r=q)']

# FORMUŁY OD SZYMONA
data = pd.read_csv('dawid=.txt')
print(data.head())
for old, new in zip(['\(p1\)', '\(p2\)', '\(p3\)', '\(p4\)'], 'pqrs'):
    data['formula'] = data['formula'].str.replace(old, new)
data['formula'] = data['formula'].str.replace(' ', '')
print(data.head())

for testseq in testSeqs[:]:
    prvr = Prover()
    seq_init = Sequent(testseq)
    prvr.pipeline(seq_init)
    print()
    print(prvr.tree[['depth', 'parent', 'value', 'operation']])
    # prvr.tree.to_excel('out_debug.xlsx')

    # check if a sequent is a tautology
    print()
    print(check_if_tautology(prvr))

    # ts = [tuple(x) for x in prvr.tree[['parent', 'value']].values]
    # # print(ts)
    # # Gm = Graph.TupleList(ts, directed=True)
    # # igraph.plot(Gm)
    # G = nx.DiGraph()
    # G.add_edges_from(ts)
    # # print(G)
    # # pos = hierarchy_pos(G, 'ROOT')
    # nx.draw(G, with_labels=True)
    # plt.savefig('out_graphs\\' + seq_init.sequent + '.png')
    # plt.close()
    print()
    print('*'*30)
    print()
#     # break
#     # https://stackoverflow.com/questions/57512155/how-to-draw-a-tree-more-beautifully-in-networkx
#
#     # g = igraph.gra
#     # fig = px.treemap(1/prvr.tree['depth'], parents=prvr.tree['parent'], values=prvr.tree['value'])
#     # fig = go.Figure()
#     # fig.add_trace(go.Treemap(parents=prvr.tree['parent'], values=prvr.tree['value']))
#     # fig.show()
#     # break
#     # print('*'*30)
#     # input()
#     # print()


# prvr = Prover()
# seq_init = Sequent(testSeqs[6])
# prvr.pipeline(seq_init)
# print()
