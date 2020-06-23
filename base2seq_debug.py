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


def seq2base(sequent):
    sequent = re.split(ss, sequent)
    print(ss.join(sequent))
    elts = [elt for side in sequent for elt in side.split(',')]

    longest_elt = str(max(elts, key=len))
    dissolve = re.findall('\((.*?)\)', longest_elt)
    if not dissolve:
        dissolve = re.split(op, longest_elt)
    print(sequent)
    sequent = [re.sub(f"\({dissolve[0]}\){op}\({dissolve[1]}\)|{dissolve[0]}{op}{dissolve[1]}",
                      f"A{op}B", side) for side in sequent]

    inv_dict = {'A': '', 'B': ''}
    lang = 'ABΓΔ'
    for w1, w2 in zip(dissolve, lang[:len(dissolve)]):
        if (not (inv_dict[w2] == '(' + w1 + ')')) and (not (inv_dict[w2] == w1)):
            possible_cuts = 'AB'
        if len(w1) > 1:
            inv_dict[w2] = ['(' + w1 + ')']
        else:
            inv_dict[w2] = [w1]
        sequent = [re.sub(f"{w1}", f"{w2}", side) for side in sequent]
    sequent = [re.sub(r"\((.?)\)", r"\1", side) for side in sequent]

    for n, side in enumerate(sequent):
        noise = lang[n + 2]
        inv_dict[noise] = re.findall(f'[^{lang}~,]+', side)
        if op in inv_dict[noise]:
            inv_dict[noise].remove(op)

        inv_dict[noise].sort(key=len, reverse=True)
        for elt in inv_dict[noise]:
            sequent[n] = re.sub('~?' + re.escape(elt), '', sequent[n])
        sequent[n] = re.sub('^,*|,*$', '', sequent[n])

        if sequent[n]:
            if n:
                sequent[n] = noise + ',' + sequent[n]
            else:
                sequent[n] = sequent[n] + ',' + noise
        else:
            sequent[n] = noise

    return ss.join(sequent), inv_dict


def base2seq(solution, inv_dict):
    for ch in 'ABΓΔ':
        solution = re.sub(ch, ','.join(inv_dict[ch]), solution)
    solution = re.sub(f',?{ss},?', ss, solution)
    print(solution)


testSeqs = ['p->p=p',
            '->p=p,p',
            '~p->p=p',
            '->p=p,~p',
            'p=q->p=r,(q=r)=(p=r)',
            'p=q,p=r->(q=r)=(p=r)',
            'p=q->~(p=r),(q=r)=(p=r)',
            'p=q,~(p=r)->(q=r)=(p=r)',
            'p,p=q,~(p=r)->(q=r)=(p=r)',
            'p,(p=q)=(s=t),~(p=r)->(q=r)=(p=r)']
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

# for test_seq in testSeqs:
#     seq = seq_format(test_seq)
#     seq_translated, inv_dict = seq2base(seq)
#     print(seq_translated)
#     base2seq(seq_translated, inv_dict)
#     print()
