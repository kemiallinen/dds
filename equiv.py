import re
from termcolor import cprint
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt


class Proofer():
    def __init__(self, sequent, rules, ss, op):
        self.sequent = sequent
        self.rules = rules
        self.ss = ss
        self.op = op
        self.lang = 'ABΓΔ'
        self.inv_dict = {'A': [], 'B': []}
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
        print('nodes checked = {}'.format(self.nodes_checked))
        print('*************\n')

        if '~' in self.sequent:
            # TODO: fix possible bug in eg. ~p o q
            self.nodes_checked.append('{}'.format(self.sequent))
            actual_parent = self.sequent
            self.negation_remover()
            self.G.add_node(self.sequent)
            self.G.add_edge(actual_parent, self.sequent)
            level += 1
            print('\n*************')
            print('[negation removed]')
            print('level = {}'.format(level))
            print('sequent = {}'.format(self.sequent))
            print('current parent = {}'.format(actual_parent))
            print('*************\n')
        print(self.sequent)
        if self.check_if_axiom():
            print('\n*************')
            print('{} is axiom'.format(self.sequent))
            print('current parent = {}'.format(actual_parent))
            print('node is closed')
            print('*************\n')

        else:
            self.nodes_checked.append('{}'.format(self.sequent))
            self.seq2base()

            print('\n*************')
            print('sequent fitted = {}'.format(self.sequent))
            print('fitting dict = {}'.format(self.inv_dict))

            if self.sequent in self.rules:
                print('[solutions from rules]')
                solutions = self.rules[self.sequent]
            else:
                print('[no rules found]')
                print('[cut]')
                solutions = self.cut()

            if type(solutions) == str:
                # solutions = list(solutions)
                solutions = [solutions]

            print('[solutions fitted] = {}'.format(solutions))
            level += 1
            for n_sol, solution in enumerate(solutions):
                print('solution {} = {}'.format(n_sol+1, self.base2seq(solution)))
            for solution in solutions:
                actual_parent = self.base2seq(self.sequent)
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

    def check_if_axiom(self):
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
        # can be thrown out of the class
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

        return sequent

    def seq2base(self):
        sequent = re.split(self.ss, self.sequent)
        elts = [elt for side in sequent for elt in side.split(',')]
        longest_elt = str(max(elts, key=len))
        dissolve = re.findall('\((.*?)\)', longest_elt)
        # print('[1]', dissolve)
        if not dissolve:
            dissolve = re.split(self.op, longest_elt)
            # print('[2]', dissolve)
        if len(dissolve) == 1:
            dissolve = [elt for elt in ','.join(sequent).split(',') if elt][:2]
        # elif len(dissolve) == 1:
        #     dissolve = re.split(self.op, dissolve[0])
        #     print('[3]', dissolve)
        # if len(dissolve) == 1:
        #     dissolve = sequent[:]
        #     print('[4]', dissolve)
        sequent = [re.sub(f"\({dissolve[0]}\){self.op}\({dissolve[1]}\)|{dissolve[0]}{self.op}{dissolve[1]}",
                          f"A{self.op}B", side) for side in sequent]
        # print(sequent)
        # print(dissolve)
        for w1, w2 in zip(dissolve, self.lang[:len(dissolve)]):
            if (not (self.inv_dict[w2] == '(' + w1 + ')')) and (not (self.inv_dict[w2] == w1)):
                self.possible_cuts = 'AB'
                # self.inv_dict = {'A': [], 'B': []}
            if len(w1) > 1:
                self.inv_dict[w2] = ['(' + w1 + ')']
            else:
                self.inv_dict[w2] = [w1]
            sequent = [re.sub(f"{w1}", f"{w2}", side) for side in sequent]
        # print(self.inv_dict)
        # print(sequent)
        sequent = [re.sub(r"\((.{0,3})\)", r"\1", side) for side in sequent]
        for n, side in enumerate(sequent):
            noise = self.lang[n + 2]
            # self.inv_dict[noise] = re.findall(f'[^{self.lang}~,]+', side)
            self.inv_dict[noise] = list(filter(lambda x: not set(x) <= set(self.lang+self.op), side.split(',')))
            # if op in self.inv_dict[noise]:
            #     self.inv_dict[noise].remove(op)
            self.inv_dict[noise].sort(key=len, reverse=True)
            for elt in self.inv_dict[noise]:
                side = re.sub('~?' + re.escape(elt), '', side)
            side = re.sub(',{2,}', ',', side)
            side = re.sub('^,*|,*$', '', side)
            if side:
                if n:
                    side = noise + ',' + side
                else:
                    side = side + ',' + noise
            else:
                side = noise
            sequent[n] = self.sort_formulas(side, n)
        # print(sequent)
#########################################################
        # dissolve = self.update_dict(sequent)
        #
        # for n, side in enumerate(sequent):
        #     print('n = ', n, ' side = ', side)
        #     if n == 0:
        #         noise = 'Γ'
        #     else:
        #         noise = 'Δ'
        #
        #     for num_elt, elt in enumerate(side):
        #         print('num_elt = ', num_elt, ' elt = ', elt)
        #         if len(self.rule_dict) > 1:
        #             side[num_elt] = re.sub(dissolve[0], self.rule_dict[dissolve[0]][0], elt)
        #             side[num_elt] = re.sub(dissolve[1], self.rule_dict[dissolve[1]][0], side[num_elt])
        #             side[num_elt] = re.sub('\(|\)', '', side[num_elt])
        #         else:
        #             side[num_elt] = re.sub(dissolve[0], self.rule_dict[dissolve[0]][0], elt, 1)
        #             side[num_elt] = re.sub(dissolve[1], self.rule_dict[dissolve[1]][1], side[num_elt], 1)
        #
        #         if not any(ch in side[num_elt] for ch in self.lang):
        #             if side[num_elt]:
        #                 self.rule_dict[side[num_elt]] = noise
        #                 self.inv_dict[noise] = side[num_elt]
        #             side[num_elt] = noise
        #
        #     sequent[n] = ','.join(side)
        #     if not any(ch in sequent[n] for ch in 'ΓΔ'):
        #         sequent[n] += ',' + noise
        #     sequent[n] = self.sort_formulas(sequent[n], n)
        # print(self.inv_dict)
        self.sequent = self.ss.join(sequent)

    def base2seq(self, solution):
        for ch in self.lang[::-1]:
            solution = re.sub(ch, ','.join(self.inv_dict[ch]), solution)
        solution = solution.split(self.ss)
        for n_side, side in enumerate(solution):
            side = side.split(',')
            for n_elt, elt in enumerate(side):
                if len(elt) == 5:
                    side[n_elt] = elt[1:4]
            solution[n_side] = ','.join(side)
        solution = self.ss.join(solution)
        return re.sub(f',?{self.ss},?', self.ss, solution)

        # for ch in 'ΓΔ':
        #     if not ch in self.inv_dict:
        #         self.inv_dict[ch] = ''
        # sol_seq = []
        # for elt in re.split(self.ss, multi_replace(self.inv_dict, solution)):
        #     sol_side = []
        #     for splt in re.split(',', elt):
        #         if (len(re.findall('\((.*?)\)', splt)) == 1) and (not splt[0] == '~'):
        #             sol_side.append(re.sub('\(|\)', '', splt))
        #         else:
        #             sol_side.append(splt)
        #     sol_seq.append(','.join(filter(None, sol_side)))
        # return self.ss.join(sol_seq)

    def sort_formulas(self, side, num_side):
        if num_side == 0:
            sort_ord = {'A': 1, 'B': 2, 'A' + self.op + 'B': 3, 'Γ': 4}
        else:
            sort_ord = {'Δ': 1, 'A': 2, 'B': 3,
                        'A' + self.op + 'B': 4,
                        'B' + self.op + 'A': 5}
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
#
# test_seq = testSeqs[6]
# test_seq = seq_format(test_seq)
# obj = Proofer(test_seq, rulesNoise, ss, op)
# obj.pipeline()

# test_seq = seq_format('p=q->p=r,(q=r)=(p=r)')
# obj = Proofer(test_seq, rulesNoise, ss, op)
# obj.pipeline()

for test_seq in testSeqs:
    test_seq = seq_format(test_seq)
    obj = Proofer(test_seq, rulesNoise, ss, op)
    obj.pipeline()
    cprint('\n' + '#'*40, "blue", end='\n\n')

    nx.nx_agraph.write_dot(obj.G, 'test.dot')

    # same layout using matplotlib with no labels
    plt.title('draw_networkx')
    pos = graphviz_layout(obj.G, prog='dot')
    nx.draw(obj.G, pos, with_labels=False, arrows=False)
    nx.draw(obj.G, with_labels=True)
    plt.show()
    input()

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
