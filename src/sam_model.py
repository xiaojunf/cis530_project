from collections import defaultdict
import simplejson as json
import math
import numpy as np
ALPHA = 1.0
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

    def get_score(sentence_idx,pos_list):
        return [calculate_feature_score(f_idx,
                                sent_pos_list[sentence_idx])
                                for f_idx in pos_list]


    feature_score_list = [dict([(f,get_score(i,v))
                    for (f,v) in fs.items()])
                    for (i,fs) in enumerate(feature_pos_list)]
    return  feature_score_list

def calculate_parameters(f_s_dict):
    feature_total = reduce(lambda x,y:x+y,map(lambda x:len(x),f_s_dict.values()))
    return  dict([(f,{'prob':float(len(v))/feature_total,
                         'mu':np.average(np.array(v)),
                         'sigma':np.var(np.array(v))})
                        for f,v in f_s_dict.items()])
    
    pass

def merge_feature_score(f_s_list):
    merge_dict = defaultdict(list)
    def add2dict(sent_dict):
        map(lambda x:merge_dict[x[0]].extend(x[1]),sent_dict.items())
    map(add2dict,f_s_list)
    return merge_dict

def sam_model(parameter,feature_sent):





    pass

def get_summary(feature_file,sentiment_file):
    f_s_list = preprocess_file(feature_file,sentiment_file)
    merge_dict = merge_feature_score(f_s_list)
    total_param = calculate_parameters(merge_dict)
    sent_param = map(calculate_parameters,f_s_list)

if __name__=='__main__':
    feature_file = './../data/sentDicts_after/ipod_Dict_2.txt'
    sentiment_file = './../data/sentiment/ipod_Sentiment.txt'
    sam_model(feature_file,sentiment_file)
