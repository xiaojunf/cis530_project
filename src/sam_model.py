from collections import defaultdict
import simplejson as json
import math
import numpy as np
import random
from scipy import integrate
ALPHA = 1.0
NUM = 7
T=1000
def calculate_feature_score(feature_idx,sent_dict):
    #position is the key, value is the sentiment word in the position
    pos_sent_dict = dict([(idx,w) for w in sent_dict.keys()
                             for idx in sent_dict[w]['index']])
    valid_pos = filter(lambda x:math.fabs(x-feature_idx)<5,
                                    pos_sent_dict.keys())

    if not valid_pos :
        return 0.0
    intensity = sum([math.fabs(sent_dict[pos_sent_dict[p]]['score'])
                                            for p in valid_pos])
    score = sum([sent_dict[pos_sent_dict[p]]['score']
                            for p in valid_pos])/(intensity+ALPHA)
    return score



def preprocess_file(feature_file,sentiment_file):
#    feature2sentence_dict = defaultdict(list)

#    feature_sent_dict.clear()
    cin = open(feature_file)
    feature_pos_list = json.loads(cin.read())
    cin.close()
    cin = open(sentiment_file)
    sent_pos_list = json.loads(cin.read())
    cin.close()

    print sent_pos_list
    print feature_pos_list
#    print sent_pos_list
    def get_score(sentence_idx,pos_list):   #pos_list is the positions the feature occur
                                            # in sentence_idx, for every pos, there is a score
        return [calculate_feature_score(f_idx,
                                sent_pos_list[sentence_idx])
                                for f_idx in pos_list]


    feature_score_list = [dict([(f,get_score(i,v))
                    for (f,v) in fs.items()])
                    for (i,fs) in enumerate(feature_pos_list)]

    intensity_list = [sum([math.fabs(fs[f]['score'])*len(fs[f]['index'])
                                                    for f in fs.keys()])
                                                    for fs in sent_pos_list]
    return  feature_score_list,intensity_list

def sam_parameters(f_s_dict):
    feature_total = reduce(lambda x,y:x+y,map(lambda x:len(x),f_s_dict.values()))
    return  dict([(f,{'prob':float(len(v))/feature_total,
                         'mu':np.average(np.array(v)),
                         'sigma':np.var(np.array(v))})
                        for f,v in f_s_dict.items()])


def merge_feature_score(f_s_list):
    merge_dict = defaultdict(list)
    def add2dict(sent_dict):
        map(lambda x:merge_dict[x[0]].extend(x[1]),sent_dict.items())
    map(add2dict,f_s_list)
    return merge_dict


def KL_divergence(total_param, summary_param):
    valid_param = filter(lambda f:
            summary_param[f]['sigma']>0.01,summary_param.keys())
    def KL_discrete(p1,p2):
        return p1*math.log(p1/p2)+(1-p1)*math.log((1-p1)/(1-p2))

    def KL_norm(mu1,mu2,sig1,sig2):
        k1 = 1/math.sqrt(2*math.pi*sig1)
        s1 = -1.0/(2*sig1)
        k2 = 1/math.sqrt(2*math.pi*sig2)
        s2 = -1.0/(2*sig2)

        def fun(x):
            return k1*(math.exp(s1*(x-mu1)*(x-mu1)))*\
                   (math.log(k1*math.exp(s1*(x-mu1)*(x-mu1))
                   /(k2*(math.exp(s2*(x-mu2)*(x-mu2))))))
        return integrate.quad(fun,-1,1)[0]
    kl = [KL_discrete(total_param[f]['prob'],summary_param[f]['prob'])
            +KL_norm(total_param[f]['mu'],summary_param[f]['mu'],
                     total_param[f]['sigma'],summary_param[f]['sigma'])
                    for f in valid_param]
    return -sum(kl)



def get_summary(feature_file,sentiment_file,sentence_file,output_file):

    cin = open(sentence_file)
    sentences = cin.readlines()
    cin.close()

    f_s_list,intensity_list = preprocess_file(feature_file,sentiment_file)

    #remove sentences with low intensity
    sentences = [s for i,s in enumerate(sentences) if intensity_list[i]>0.0]
    f_s_list = [f for i,f in enumerate(f_s_list) if intensity_list[i] >0.0]

    merge_dict = merge_feature_score(f_s_list)
    total_param = sam_parameters(merge_dict)


    # remove useless features
    valid_features = [f for f,v in total_param.items()
                        if v['sigma']!=0 or v['mu']!=0]
    f_s_list = [dict([(f,v) for f,v in f_dict.items()
                            if f in valid_features])
                            for f_dict in f_s_list]
    #remove sentences with no features
    sentences = [s for i,s in enumerate(sentences) if len(f_s_list[i])>0]
    f_s_list = [f for f in f_s_list if len(f)>0]

    merge_dict = merge_feature_score(f_s_list)
    total_param = sam_parameters(merge_dict)


    #initial summary
    sent_list = range(len(f_s_list))
    random.shuffle(sent_list)
    old_summary = [f_s_list[i] for i in sent_list[:NUM]]
    merge_dict = merge_feature_score(old_summary)
    summary_param = sam_parameters(merge_dict)

    oldE = KL_divergence(total_param,summary_param)

    def swap(i,j):
        temp=sent_list[i]
        sent_list[i] = sent_list[j]
        sent_list[j] = temp

    P=0.8
    for t in range(T):
#        print sent_list[:5]
        i = random.randrange(0,NUM)
        j = random.randrange(NUM,len(sent_list))

        swap(i,j)

        new_summary = [f_s_list[i] for i in sent_list[:NUM]]
        merge_dict = merge_feature_score(new_summary)
        summary_param = sam_parameters(merge_dict)

        E = KL_divergence(total_param,summary_param)

        diffE = E-oldE
        if diffE >= 0:
#            print "swap"
            oldE = E
#            old_summary = new_summary
        else:
            r = random.random()
            if r > P:
                swap(i,j)
            else:
#                print "swap"
                oldE = E
#                old_summary = new_summary
                
        P *=0.99

    cout = open(output_file,'w')
    for i in range(NUM):
        cout.write(sentences[sent_list[i]])
    cout.close()

    return valid_features







#    sent_param = map(calculate_parameters,f_s_list)

if __name__=='__main__':
    import os

    feature_dir = './../data/sentDicts_after'
    sentiment_dir = './../data/sentiment'
    sentence_dir = './../data/featureSentsOnly'
    summary_dir = './../data/summary'
    valid_feature_dir = './../data/features'

    feature_files = sorted([os.path.join(feature_dir,f) for f in os.listdir(feature_dir)
                            if f.endswith('.txt')])

    sentiment_files = sorted([os.path.join(sentiment_dir,f) for f in os.listdir(sentiment_dir)
                            if f.endswith('.txt')])
    sentence_files = sorted([os.path.join(sentence_dir,f) for f in os.listdir(sentence_dir)
                            if f.endswith('.txt')])

    for i in range(len(feature_files)):
        output_file = os.path.join(summary_dir,feature_files[i].split('/')[-1].split('_')[0]+'.summary')
        valid_feature = os.path.join(valid_feature_dir,feature_files[i].split('/')[-1].split('_')[0]+'.features')

        features = get_summary(feature_files[i],sentiment_files[i],sentence_files[i],output_file)

        cout = open(valid_feature,'w')
        cout.write(json.dumps(features))
        cout.close()

#    print feature_files
#    print sentiment_files
#    print sentence_files
#    feature_file = './../data/sentDicts_after/ipod_Dict_2.txt'
#    sentiment_file = './../data/sentiment/ipod_Sentiment.txt'
#    sentence_file = './../data/featureSentsOnly/ipod_featSentOnly.txt'
#    output_file = './../data/ipod.summary'
#    get_summary(feature_file,sentiment_file,sentence_file,output_file)
