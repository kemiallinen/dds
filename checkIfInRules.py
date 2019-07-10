import re
from itertools import chain
import random


class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


class RuleChecker:
    def __init__(self, test_seq):
        self.rulesNoise = {'B,A≡B,Γ⇒Δ': ['A,B,Γ⇒Δ 01',
                                    'A,A≡B,Γ⇒Δ 02'],
                      'Γ⇒Δ,A,A≡B': ['B,Γ⇒Δ,A≡B 03',
                                    'B,Γ⇒Δ,A 04'],
                      'Γ⇒Δ,B,A≡B': ['A,Γ⇒Δ,A≡B 05',
                                    'A,Γ⇒Δ,B 06'],
                      'B,Γ⇒Δ,A≡B': ['B,Γ⇒Δ,A 07',
                                    'Γ⇒Δ,A,A≡B 08'],
                      'A,Γ⇒Δ,A≡B': ['A,Γ⇒Δ,B 09',
                                    'Γ⇒Δ,B,A≡B 10'],
                      'A,Γ⇒Δ,B': ['Γ⇒Δ,B,A≡B 11',
                                  'A,Γ⇒Δ,A≡B 12'],
                      'A≡B,Γ⇒Δ,A': ['A≡B,Γ⇒Δ,B 13',
                                    'Γ⇒Δ,A,B 14'],
                      'A,A≡B,Γ⇒Δ': ['A,B,Γ⇒Δ 15',
                                    'B,A≡B,Γ⇒Δ 16'],
                      'A≡B,Γ⇒Δ,B': ['Γ⇒Δ,A,B 17',
                                    'A≡B,Γ⇒Δ,A 18'],
                      'A,B,Γ⇒Δ,A≡B': ['A,A≡B,Γ⇒Δ,B 19',
                                      'B,A≡B,Γ⇒Δ,A 20',
                                      'Γ⇒Δ,A,B,A≡B 21'],
                      'B,A≡B,Γ⇒Δ,A': ['Γ⇒Δ,A,B,A≡B 22',
                                      'A,B,Γ⇒Δ,A≡B 23'],
                      'A,A≡B,Γ⇒Δ,B': ['Γ⇒Δ,A,B,A≡B 24',
                                      'B,A≡B,Γ⇒Δ,A 25',
                                      'A,B,Γ⇒Δ,A≡B 26'],
                      'Γ⇒Δ,A,B,A≡B': ['A,B,Γ⇒Δ,A≡B 27',
                                      'B,A≡B,Γ⇒Δ,A 28'],
                      'A,B,Γ⇒Δ': ['B,A≡B,Γ⇒Δ 29'],
                      'B,Γ⇒Δ,A': ['Γ⇒Δ,A,A≡B 30',
                                  'B,Γ⇒Δ,A≡B 31'],
                      'Γ⇒Δ,A,B': ['A≡B,Γ⇒Δ,B 32']}

        self.ss = '⇒'
        self.op = '≡'
        self.sequent = seq_format(test_seq, self.ss, self.op)

        self.lang = 'ABΓΔ'
        self.rule_dict = Dictlist()
        self.inv_dict = {'A': '', 'B': ''}
        self.output = []
        self.dissolve = []

        self.seq2base()
        if self.sequent in self.rulesNoise:
            solutions = self.rulesNoise[self.sequent]
            for num_sol, solution in enumerate(solutions):
                self.output.append([self.base2seq(solution[:-3]), solution[-2:]])

    def seq2base(self):
        self.sequent = re.split(self.ss, self.sequent)

        self.update_dict()

        for n, side in enumerate(self.sequent):
            if n == 0:
                noise = 'Γ'
            else:
                noise = 'Δ'

            for num_elt, elt in enumerate(side):
                if len(self.rule_dict) > 1:
                    side[num_elt] = re.sub(self.dissolve[0], self.rule_dict[self.dissolve[0]][0], elt)
                    side[num_elt] = re.sub(self.dissolve[1], self.rule_dict[self.dissolve[1]][0], side[num_elt])
                    side[num_elt] = re.sub('\(|\)', '', side[num_elt])
                else:
                    side[num_elt] = re.sub(self.dissolve[0], self.rule_dict[self.dissolve[0]][0], elt, 1)
                    side[num_elt] = re.sub(self.dissolve[1], self.rule_dict[self.dissolve[1]][1], side[num_elt], 1)

                if not any(ch in side[num_elt] for ch in self.lang):
                    if side[num_elt]:
                        self.rule_dict[side[num_elt]] = noise
                        self.inv_dict[noise] = side[num_elt]
                    side[num_elt] = noise

                    self.sequent[n] = ','.join(side)
            if not any(ch in self.sequent[n] for ch in 'ΓΔ'):
                self.sequent[n] += noise
                self.sequent[n] = ','.join(self.sequent[n])
            self.sequent[n] = self.sort_formulas(self.sequent[n], n)

        self.sequent = self.ss.join(self.sequent)

    def base2seq(self, solution):
        for ch in 'ΓΔ':
            if ch not in self.inv_dict:
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

    def update_dict(self):
        for n, side in enumerate(self.sequent):
            self.sequent[n] = re.split(',', side)
        lens = []
        elts = []
        for elt in chain.from_iterable(self.sequent):
            lens.append(len(elt))
            elts.append(elt)
        if (len(set(lens)) == 1) and not (len(set(re.findall('[a-z]', ''.join(elts)))) <= 2):
            self.dissolve = random.sample(elts, 2)
        else:
            longest_elt = max(chain.from_iterable(self.sequent), key=len)
            self.dissolve = re.findall('\((.*?)\)', longest_elt)
            if not self.dissolve:
                self.dissolve = re.split(self.op, longest_elt)

        self.rule_dict = Dictlist()
        for w1, w2 in zip(self.dissolve, self.lang[:len(self.dissolve)]):
            if len(w1) > 1:
                self.rule_dict[w1] = w2
                self.inv_dict[w2] = '(' + w1 + ')'
            else:
                self.rule_dict[w1] = w2
                self.inv_dict[w2] = w1

    def sort_formulas(self, side, num_side):
        if self.op == '≡':
            side = side.replace('B≡A', 'A≡B')
        if num_side == 0:
            sort_ord = {'A': 1, 'B': 2, 'A' + self.op + 'B': 3, 'Γ': 4}
        else:
            sort_ord = {'Δ': 1, 'A': 2, 'B': 3, 'A' + self.op + 'B': 4, 'B' + self.op + 'A': 5}
        to_sort = re.split(',', side)
        to_sort_num = []
        for elt in to_sort:
            to_sort_num.append(sort_ord[elt])
        to_sort = zip(to_sort_num, to_sort)
        return ','.join([x for _, x in sorted(to_sort)])


def multi_replace(dictionary, text):
    """
    http://code.activestate.com/recipes/81330-single-pass-multiple-replace/
    :param dictionary:  dict of keys to be replaced by respective values
    :param text:        input string on which we perform replacement
    :return:            string with replaced values
    """
    regex = re.compile('(%s)' % '|'.join(map(re.escape, dictionary.keys())))
    return regex.sub(lambda mo: dictionary[mo.string[mo.start():mo.end()]], text)


def seq_format(sequent, ss, op):
    dictionary = {'->': ss,
                  '=': op}
    return multi_replace(dictionary, sequent)


test_seq = 'p->p=q'
rc = RuleChecker(test_seq)

for line in rc.output:
    print(line)
