from nltk.corpus import wordnet as wn
from operator import itemgetter
import math
syn_words={}
ant_words={}
def get_syn_ant_words(word_tag):
    try:
        return syn_words[word_tag],ant_words[word_tag]
    except KeyError:
        w,i = word_tag.split('__')
        syn_sets = wn.synsets(w,i)
        syn_words[word_tag]=set([lemma.name+'__'+i
                    for synset in syn_sets
                    for lemma in synset.lemmas ])
        ant_words[word_tag]=set([a_lemma.name+'__'+i
                            for synset in syn_sets
                            for lemma in synset.lemmas
                            for a_lemma in lemma.antonyms()])
        return syn_words[word_tag],ant_words[word_tag]

def one_round(pre_words,lam,M):
    cur_words={}
    get = cur_words.get
    def add2dict(word):
        if word not in M:
            syn,ant = get_syn_ant_words(word)
            for w in syn:
                factor = 1+lam if word==w else lam
                cur_words[w]=get(w,0)+pre_words[word]*factor
            for w in ant:
                factor = -lam
                cur_words[w]=get(w,0)+pre_words[word]*factor
    map(add2dict,pre_words.keys())

    return cur_words

def calculate_sensitive_score(neg_file,pos_file,neu_file):
    N = open(neg_file).read().split('\t')
    P = open(pos_file).read().split('\t')
    M = open(neu_file).read().split('\t')
    print M
    M = [w.split('__')[0] for w in M]
    cur_words = dict([(w,1) for w in N]+[(w,-1) for w in P])
    lam=0.2
    for i in range(5):
        print i
        cur_words = one_round(cur_words,lam,M)

    out = open('result.txt','w')

    for (w,s) in sorted(cur_words.items(),
                        key=itemgetter(1),reverse=True):
        w = w.split('__')[0]
        if w not in M and math.fabs(s)>1:
            s = math.log(math.fabs(s)) if s>0 else -math.log(math.fabs(s))
            out.write('%s\t%f\n' %(w, round(s,2)))
    out.close()

    
if __name__=='__main__':
    calculate_sensitive_score('neg.txt','pos.txt','neu.txt')
#    out=open('pos.txt','w')
#    out.write('good__a\tamazing__a')
#    out.close()
#    out=open('neg.txt','w')
#    out.write('terrible__a\tkill__v')
#    out.close()
#    out=open('neu.txt','w')
#    out.write('that\the\tshe')
#    out.close()
#    syn_words['a']=set(['a'])
#    ant_words['a']=set(['d'])
#
#    syn_words['b']=set(['b','c'])
#    ant_words['b']=set([])
#
#    syn_words['c']=set(['c','b'])
#    ant_words['c']=set([])
#    syn_words['d']=set(['e'])
#    ant_words['d']=set(['a'])
#
#    syn_words['e']=set(['d'])
#    ant_words['e']=set([])
#    cur_words = {'a':1,'b':-1,'d':0}
#    M=['d']
#    for i in range(3):
#     cur_words = one_round(cur_words,0.2,M)
#     print cur_words




  