import re
from itertools import chain
import random
import matplotlib.pyplot as plt
import networkx as nx
# from networkx.drawing.nx_agraph import graphviz_layout


class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


class Proofer():
    def __init__(self, sequent, rules, ss, op):
        self.sequent = sequent
        self.rules = rules
        self.ss = ss
        self.op = op
        self.lang = 'ABΓΔ'
        self.rule_dict = Dictlist()
        self.inv_dict = {'A': '', 'B': ''}
        self.cut_formula = ''
        self.possible_cuts = 'AB'
        self.nodes_checked = []
        self.G = nx.DiGraph()
        self.G.add_node('ROOT')

    def pipeline(self, level=1, actual_parent='ROOT'):
        self.G.add_node(self.sequent)
        self.G.add_edge(actual_parent, self.sequent)
        print('\n*************')
        print('level = {}'.format(level))
        print('sequent = {}'.format(self.sequent))
        print('current parent = {}'.format(actual_parent))
        print('*************\n')

        if self.check_if_tautology():
            print('\n*************')
            print('{} is tautology'.format(self.sequent))
            print('current parent = {}'.format(actual_parent))
            print('node is closed')
            print('*************\n')

        else:
            self.nodes_checked.append('{}'.format(self.sequent))

            if '~' in self.sequent:
                actual_parent = self.sequent
                self.negation_remover()
                self.G.add_node(self.sequent)
                self.G.add_edge(actual_parent, self.sequent)
                level += 1
                self.nodes_checked.append('{}'.format(self.sequent))
                print('\n*************')
                print('[negation removed]')
                print('level = {}'.format(level))
                print('sequent = {}'.format(self.sequent))
                print('current parent = {}'.format(actual_parent))
                print('*************\n')

            self.seq2base()

            print('\n*************')
            print('sequent fitted = {}'.format(self.sequent))
            print('fitting dict = {}'.format(self.rule_dict))

            if self.sequent in self.rules:
                print('[solutions from rules]')
                solutions = self.rules[self.sequent]
            else:
                print('[no rules found]')
                print('[cut]')
                solutions = self.cut()

            if type(solutions) == str:
                solutions = list(solutions)

            print('[solutions fitted] = {}'.format(solutions))

            for n_sol, solution in enumerate(solutions):
                print('solution {} = {}'.format(n_sol+1, self.base2seq(solution)))
            print('*************\n')

            actual_parent = self.base2seq(self.sequent)
            level += 1

            for solution in solutions:
                self.sequent = self.base2seq(solution)
                if not (self.sequent in self.nodes_checked):
                    self.pipeline(level, actual_parent)
                else:
                    self.G.add_node(self.sequent)
                    self.G.add_edge(actual_parent, self.sequent)
                    print('\n*************')
                    print('node {} already checked'.format(self.sequent))
                    print('level = {}'.format(level))
                    print('*************\n')

    def check_if_tautology(self):
        if set(re.split(',', self.sequent.split(self.ss)[0])) & set(re.split(',', self.sequent.split(self.ss)[1])):
            return True
        else:
            return False

    def negation_remover(self):
        sequent = re.split(self.ss, self.sequent)
        for rd in ['~[A-Za-z]', '~\((\(.*?\))\)', '~\((.*?)\)']:
            for n, side in enumerate(sequent):
                sequent = self.negs_replace(re.findall(rd, side), sequent, n)
        self.sequent = ss.join(sequent)

    def negs_replace(self, negs, sequent, n):
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

    def seq2base(self):
        sequent = re.split(self.ss, self.sequent)

        dissolve = self.update_dict(sequent)

        for n, side in enumerate(sequent):
            if n == 0:
                noise = 'Γ'
            else:
                noise = 'Δ'

            for num_elt, elt in enumerate(side):
                if len(self.rule_dict) > 1:
                    side[num_elt] = re.sub(dissolve[0], self.rule_dict[dissolve[0]][0], elt)
                    side[num_elt] = re.sub(dissolve[1], self.rule_dict[dissolve[1]][0], side[num_elt])
                    side[num_elt] = re.sub('\(|\)', '', side[num_elt])
                else:
                    side[num_elt] = re.sub(dissolve[0], self.rule_dict[dissolve[0]][0], elt, 1)
                    side[num_elt] = re.sub(dissolve[1], self.rule_dict[dissolve[1]][1], side[num_elt], 1)

                if not any(ch in side[num_elt] for ch in self.lang):
                    if side[num_elt]:
                        self.rule_dict[side[num_elt]] = noise
                        self.inv_dict[noise] = side[num_elt]
                    side[num_elt] = noise

            sequent[n] = ','.join(side)
            if not any(ch in sequent[n] for ch in 'ΓΔ'):
                sequent[n] += ',' + noise
            sequent[n] = self.sort_formulas(sequent[n], n)

        self.sequent = self.ss.join(sequent)

    def base2seq(self, solution):
        for ch in 'ΓΔ':
            if not ch in self.inv_dict:
                self.inv_dict[ch] = ''
        sol_seq = []
        for elt in re.split(self.ss, multi_replace(self.inv_dict, solution)):
            sol_side = []
            for splt in re.split(',', elt):
                if (len(re.findall('\((.*?)\)', splt)) == 1) and (not splt[0] == '~'):
                    sol_side.append(re.sub('\(|\)', '', splt))
                else:
                    sol_side.append(splt)
            sol_seq.append(','.join(filter(None, sol_side)))
        return self.ss.join(sol_seq)

    def update_dict(self, sequent):
        for n, side in enumerate(sequent):
            sequent[n] = re.split(',', side)
        lens = []
        elts = []
        for elt in chain.from_iterable(sequent):
            lens.append(len(elt))
            elts.append(elt)
        if (len(set(lens)) == 1) and not(len(set(re.findall('[a-z]', ''.join(elts))))<=2):
            dissolve = random.sample(elts, 2)
        else:
            longest_elt = max(chain.from_iterable(sequent), key=len)
            dissolve = re.findall('\((.*?)\)', longest_elt)
            if not dissolve:
                dissolve = re.split(self.op, longest_elt)
        dissolve = dissolve[::-1]
        self.rule_dict = Dictlist()
        for w1, w2 in zip(dissolve, self.lang[:len(dissolve)]):
            if not (self.inv_dict[w2] == '(' + w1 + ')'):
                if not (self.inv_dict[w2] == w1):
                    self.possible_cuts = 'AB'

            if len(w1) > 1:
                self.rule_dict[w1] = w2
                self.inv_dict[w2] = '(' + w1 + ')'
            else:
                self.rule_dict[w1] = w2
                self.inv_dict[w2] = w1
        return dissolve

    def sort_formulas(self, side, num_side):
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

    def cut(self):
        sequent_to_cut = self.sequent.split(self.ss)
        self.cut_formula = '~' + self.possible_cuts[0]
        try:
            self.possible_cuts = self.possible_cuts[1:]
        except IndexError:
            self.possible_cuts = ''
        sequents_after_cut = [self.ss.join([sequent_to_cut[0], sequent_to_cut[1] + ',' + self.cut_formula]),
                              self.ss.join([self.cut_formula + ',' + sequent_to_cut[0], sequent_to_cut[1]])]
        return sequents_after_cut


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


# '=' is the equivalence for the purpose of a user-friendly input
testSeqs = ['p->p=p',
            '->p=p,p',
            '~p->p=p',
            '->p=p,~p',
            'p=q->p=r,(q=r)=(p=r)',
            'p=q,p=r->(q=r)=(p=r)',
            'p=q->~(p=r),(q=r)=(p=r)',
            'p=q,~(p=r)->(q=r)=(p=r)']
rulesNoise = {'B,A≡B,Γ⇒Δ':      ['A,B,Γ⇒Δ',
                                 'A,A≡B,Γ⇒Δ'],
              'Γ⇒Δ,A,A≡B':      ['B,Γ⇒Δ,A≡B',
                                 'B,Γ⇒Δ,A'],
              'Γ⇒Δ,B,A≡B':      ['A,Γ⇒Δ,A≡B',
                                 'A,Γ⇒Δ,B'],
              'B,Γ⇒Δ,A≡B':      ['B,Γ⇒Δ,A',
                                 'Γ⇒Δ,A,A≡B'],
              'A,Γ⇒Δ,A≡B':      ['A,Γ⇒Δ,B',
                                 'Γ⇒Δ,B,A≡B'],
              'A,Γ⇒Δ,B':        ['Γ⇒Δ,B,A≡B',
                                 'A,Γ⇒Δ,A≡B'],
              'A≡B,Γ⇒Δ,A':      ['A≡B,Γ⇒Δ,B',
                                 'Γ⇒Δ,A,B'],
              'A,A≡B,Γ⇒Δ':      ['A,B,Γ⇒Δ',
                                 'B,A≡B,Γ⇒Δ'],
              'A≡B,Γ⇒Δ,B':      ['Γ⇒Δ,A,B',
                                 'A≡B,Γ⇒Δ,A'],
              'A,B,Γ⇒Δ,A≡B':    ['A,A≡B,Γ⇒Δ,B',
                                 'B,A≡B,Γ⇒Δ,A',
                                 'Γ⇒Δ,A,B,A≡B'],
              'B,A≡B,Γ⇒Δ,A':    ['Γ⇒Δ,A,B,A≡B',
                                 'A,B,Γ⇒Δ,A≡B'],
              'A,A≡B,Γ⇒Δ,B':    ['Γ⇒Δ,A,B,A≡B',
                                 'B,A≡B,Γ⇒Δ,A',
                                 'A,B,Γ⇒Δ,A≡B'],
              'Γ⇒Δ,A,B,A≡B':    ['A,B,Γ⇒Δ,A≡B',
                                 'B,A≡B,Γ⇒Δ,A'],
              'A,B,Γ⇒Δ':        'B,A≡B,Γ⇒Δ',
              'B,Γ⇒Δ,A':        ['Γ⇒Δ,A,A≡B',
                                 'B,Γ⇒Δ,A≡B'],
              'Γ⇒Δ,A,B':        'A≡B,Γ⇒Δ,B'}
ss = '⇒'
op = '≡'

# test_seq = testSeqs[4]
# test_seq = '->(p=q)=(q=p)'
test_seq = '->p=p'
test_seq = seq_format(test_seq)
obj = Proofer(test_seq, rulesNoise, ss, op)
obj.pipeline()

# nx.nx_agraph.write_dot(obj.G, 'test.dot')

# same layout using matplotlib with no labels
# plt.title('draw_networkx')
# pos = graphviz_layout(obj.G, prog='dot')
# nx.draw(obj.G, pos, with_labels=False, arrows=False)
nx.draw(obj.G, with_labels=True)
plt.show()

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
