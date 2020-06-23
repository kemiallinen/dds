import re


def negation_remover(sequent):
    sequent = re.split(ss, sequent)
    print('[NRem] #1 after split = ', sequent)
    for rd in ['~[A-Za-z]', '~\((\(.*?\))\)', '~\((.*?)\)']:
        for n, side in enumerate(sequent):
            sequent = negs_replace(re.findall(rd, side), sequent, n)
            print('[NRem] #8 seq after [NRep] = ', sequent)
    print('[NRem] #9 seq after loop = ', sequent)
    return ss.join(sequent)


def negs_replace(negs, sequent, n):
    print('[NRep] #2 seq in negs replace = ', sequent)
    for neg in negs:
        print('NEG = ', neg)
        if set([neg, '~(' + neg + ')']).intersection(set([item for side in sequent for item in side.split(',')])):
            to_replace = []
            if len(neg) == 2:
                to_replace = neg
                neg = neg[1]
            print('[NRep] #3 neg = ', neg)
            if sequent[int(not n)]:
                if neg not in sequent[int(not n)].split(','):
                    sequent[int(not n)] += ',' + neg
            else:
                sequent[int(not n)] += neg
            if not to_replace:
                to_replace = '~(' + neg + ')'
            print('[NRep] #4 to replace = ', to_replace)
            print('[NRep] #5 seq in neg loop = ', sequent)
            sequent[n] = sequent[n].replace(to_replace, '')
            print('[NRep] #6 seq after replace = ', sequent)
            sequent[n] = ','.join(filter(None, re.split(',', sequent[n])))
            print('[NRep] #7 seq after join = ', sequent)

    return sequent


ss = '⇒'
op = '≡'
sequent = 'p≡q⇒p≡r,(q≡r)≡(p≡r),~(q≡r)'
print(negation_remover(sequent))
