import re
import pandas as pd

# def negation_remover(sequent):
#     sequent = re.split(ss, sequent)
#     print('[NRem] #1 after split = ', sequent)
#     for rd in ['~[A-Za-z]', '~\((\(.*?\))\)', '~\((.*?)\)']:
#         for n, side in enumerate(sequent):
#             sequent = negs_replace(re.findall(rd, side), sequent, n)
#             print('[NRem] #8 seq after [NRep] = ', sequent)
#     print('[NRem] #9 seq after loop = ', sequent)
#     return ss.join(sequent)


# def negs_replace(negs, sequent, n):
#     print('[NRep] #2 seq in negs replace = ', sequent)
#     for neg in negs:
#         print('NEG = ', neg)
#         if set([neg, '~(' + neg + ')']).intersection(set([item for side in sequent for item in side.split(',')])):
#             to_replace = []
#             if len(neg) == 2:
#                 to_replace = neg
#                 neg = neg[1]
#             print('[NRep] #3 neg = ', neg)
#             if sequent[int(not n)]:
#                 if neg not in sequent[int(not n)].split(','):
#                     sequent[int(not n)] += ',' + neg
#             else:
#                 sequent[int(not n)] += neg
#             if not to_replace:
#                 to_replace = '~(' + neg + ')'
#             print('[NRep] #4 to replace = ', to_replace)
#             print('[NRep] #5 seq in neg loop = ', sequent)
#             sequent[n] = sequent[n].replace(to_replace, '')
#             print('[NRep] #6 seq after replace = ', sequent)
#             sequent[n] = ','.join(filter(None, re.split(',', sequent[n])))
#             print('[NRep] #7 seq after join = ', sequent)
#
#     return sequent
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
    if '->' not in sequent:
        sequent = '->' + sequent
    dictionary = {'->': '⇒',
                  '=': '≡'}
    return multi_replace(dictionary, sequent)


def negation_remover(sequent):
    print(f'sequent = {sequent}')
    sequent = re.split('⇒', sequent)
    print(f'nr // seq after split = {sequent}')
    # ['~[A-Za-z]', '~\((\(.*?\))\)', '~\((.*)\)', '~\((.*?)\)']
    for rd in ['~\((.*?)\)', '~[A-Za-z]']:
        print('rd =', rd)
        # while True:
        #     terminate = True
        for n, side in enumerate(sequent):
            print(f'n = {n}, side = {side}')
            negs = re.findall(rd, side)
            print(f'negs = {negs}')
            for neg in negs:
                print(f'neg = {neg}')
                print('inner list =', [item for side in sequent for item in side.split(',')])
                print('set of the above =', set([item for side in sequent for item in side.split(',')]))
                print('neg_set =', {neg, '~(' + neg + ')', '~' + neg})
                print('intersection = ', {neg, '~(' + neg + ')'}.intersection(set([item for side in sequent for item in side.split(',')])))
                if {neg, '~(' + neg + ')', '~' + neg}.intersection(set([item for side in sequent for item in side.split(',')])):
                    if len(neg) == 2:
                        print('len == 2')
                        to_replace = neg
                        neg = neg[1]
                    else:
                        to_replace = '~(' + neg + ')'
                    print('to replace: ', to_replace)
                    if sequent[int(not n)]:
                        if neg not in sequent[int(not n)].split(','):
                            sequent[int(not n)] += ',' + neg
                    else:
                        sequent[int(not n)] += neg
                    print('sequent before replace and join = ', sequent)
                    sequent[n] = sequent[n].replace(to_replace, '')
                    print('sequent after replace and before join = ', sequent)
                    sequent[n] = ','.join(filter(None, re.split(',', sequent[n])))
                    print('sequent after replace and join = ', sequent)
                    terminate = False
            # if terminate or all(['~' not in elt for elt in sequent]):
            #     break
            # input()
    return '⇒'.join(sequent)


testSeqs = ['~p->p=p',
            '->p=p,~p',
            'p=q->~(p=r),(q=r)=(p=r)',
            'p=q,~(p=r)->(q=r)=(p=r)',
            'p=q->p=r,(q=r)=(p=r),~(q=r)',
            '->~p',
            '->~(~p)',
            '->~(~(~p))',
            '->~(~(~(~p)))',
            '->~(~(~(~(~(~(~(~(~(~p)))))))))']
# ss = '⇒'
# op = '≡'
#
# data = pd.read_csv('dawid=.txt')
# for old, new in zip(['\(p1\)', '\(p2\)', '\(p3\)', '\(p4\)'], 'pqrs'):
#     data['formula'] = data['formula'].str.replace(old, new)
# data['formula'] = data['formula'].str.replace(' ', '')

rds = ['~\((.*)\)', '~\((.*?)\)', '~([A-Za-z])']
#
for ts in testSeqs:
    print(ts)
    print([re.findall(rd, ts) for rd in rds])
    print()

# for testseq in testSeqs[:]: #data['formula']:
#     print([re.findall(rd, testseq) for rd in rds])
#     print()
#     print(negation_remover(seq_format(testseq)))
#     print()
