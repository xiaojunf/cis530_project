import csv
import jpype
import nltk
import simplejson as json


word_sent_dict = nltk.defaultdict(set) #every word apear to several sentenese, key is word,
                                        # value is a list of index which imply the sentences
                                      # the word occurs
feature_sent_list = []
def preprocess_file(input_file,output_file):
    cin = open(input_file)
    feature_sent_list.extend(filter(lambda x:len(x)>0,
                               json.loads(cin.read())))
    cin.close()
    itemsets = [filter(lambda w:w.isalpha(),line.keys())
                for line in feature_sent_list]
#    print itemsets


    def add2dict((idx,words)):
        map(lambda x: word_sent_dict[x].add(idx), words)
    map(add2dict,enumerate(itemsets))
    word_set = list(set(reduce(lambda x,y:x+y,itemsets)))

    print len(word_set)
#    global word_dict
    word_dict = dict([(w,i) for i,w in enumerate(word_set)])


    item_map = [[word_dict[w] for w in line] for line in itemsets]

    cout = open(output_file,'wb')
    csvWriter = csv.writer(cout,dialect='excel',quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(word_set)
    for item in item_map:
        line = ['?']*len(word_set)

        def trans_mark(i):
            line[i]='yes'
        map(trans_mark,item)
        csvWriter.writerow(line)
    cout.close()

def startJvm():
    import os
    os.environ.setdefault("LIB_HOME", "./../lib")
    global lib_home
    lib_home = os.environ["LIB_HOME"]
    jpype.startJVM(jpype.getDefaultJVMPath(),
                   "-ea",
                  "-Djava.class.path=%s/weka.jar" %lib_home)

#startJvm() # one jvm per python instance.

def get_instances(csv_file):
    global package_core
    global package_io
    package_io = jpype.java.io
    package_core = jpype.JPackage("weka.core")
    package_converters = package_core.converters
    csvloader = package_converters.CSVLoader()
    csvloader.setSource(package_io.File(csv_file))

    return csvloader.getDataSet()


def apriori(instances):
    associator = jpype.JPackage('weka.associations').Apriori()
    associator.setLowerBoundMinSupport(0.01)
    associator.buildAssociations(instances)
    itemsets_vector = [[item.toString(instances) for item in itemset]
                for itemset in associator.__getattribute__('m_Ls')]
    print "itemsets_vector===",itemsets_vector
    print len(itemsets_vector)
    itemsets_vector = itemsets_vector[:3]

    import re
    def string2words(s):
        return ' '.join(re.findall(r'(\w+)=',s))

    return [map(string2words, itemset) for itemset in itemsets_vector]

def get_high_freq(array):
    array_dict = dict([(x,array.count(x)) for x in set(array)])
    return sorted(array_dict.keys(),
                  key=array_dict.__getitem__,reverse=True)[0]


def compactness_pruning(itemsets):

    def check_compact(feature):
        nouns = feature.split()
        all_occur = reduce(lambda x,y:x.intersection(y),[word_sent_dict[n] for n in nouns])
        def check_position(sent_idx):
            sent = feature_sent_list[sent_idx]
            words_order = dict([(idx, w) for w in sent.keys() for idx in sent[w]])
            if len(nouns)==2:
                pos_comb = [sorted([x,y]) for x in sent[nouns[0]]
                                  for y in sent[nouns[1]]]
                pos_comb = filter(lambda x:x[1]-x[0]<3, pos_comb)


            if len(nouns)==3:
                pos_comb = [sorted([x,y,z]) for x in sent[nouns[0]]
                                  for y in sent[nouns[1]]
                                  for z in sent[nouns[2]]]
#                print pos_comb
                pos_comb = filter(lambda x:x[1]-x[0]<2 and x[2]-x[1]<2, pos_comb)
            if len(pos_comb)>0:
                phrase = ' '.join(map(lambda x:words_order[x],pos_comb[0]))
                return phrase
        if len(all_occur)>1:
            phrase_order = filter(lambda x: x!=None,map(check_position, all_occur))
#            print phrase_order
            if len(phrase_order)>1:
                return get_high_freq(phrase_order)
#    print itemsets[2]
    itemset_2 = None
    itemset_3 = None
    if len(itemsets)>1:
        itemset_2 = filter(lambda x: x!=None,map(check_compact,itemsets[1]))
    if len(itemsets)>2:
        itemset_3 = filter(lambda x: x!=None,map(check_compact,itemsets[2]))
    return itemset_2,itemset_3
    pass


def redundant_pruning(itemsets):
    cur_itemsets = list(itemsets)
    cur_dict = dict(word_sent_dict)


    def remove_word_sent(pair):
        pair = pair.split()
        intersect = word_sent_dict[pair[0]].intersection \
                                (word_sent_dict[pair[1]])
        cur_dict[pair[0]]=cur_dict[pair[0]]-intersect
        cur_dict[pair[1]]=cur_dict[pair[1]]-intersect
    map(remove_word_sent, cur_itemsets[1])
    return filter(lambda x:len(cur_dict[x])>3,
                                        cur_itemsets[0])

'''
TO Halston:
Since I use java package, like weka, so you may have to install
jpype in your computer first.

get_frequent_feature is the main method you may want to use
input_file is the file generated by you, in the format that
every line has several nouns seperated by \t, note: only noun
no phrases, if there are phrases just consider it as several
words, and phrases will be generated by association

output_file is the frequent features, which is in json format,
so that you can simply use json.loads(open(file_name).read())
to transform the file into a dictionary, and itemset_i is the
feature with i words

I only have done the redundant pruning for single word feature,
and haven't done compactness pruning, and for the noun phrases,
Since the association doesn't consider the position of the word,
so battery life may become life battery, I will fix that in the
future.

'''

def get_frequent_features(input_file,output_file): #TODO compactness pruning
    csv_file = './../data/intermediate.csv'
    preprocess_file(input_file,csv_file)
    instances = get_instances(csv_file)
    itemsets = apriori(instances)
#    jpype.shutdownJVM()
    
    itemset_1 = redundant_pruning(itemsets)

    itemset_2,itemset_3 = compactness_pruning(itemsets)
    print itemset_2
    print itemset_3
    content = json.dumps({'itemset_1':itemset_1,
                         'itemset_2':itemset_2,
                         'itemset_3':itemset_3})
    cout = open(output_file,'w')
    cout.write(content)
    cout.close()

if __name__=='__main__':
#    startJvm()
#    input_file = './../data/sentDicts/Apex_AD2600_Progressive-scan_DVD_player_Dict_2.txt'
#    output_file = input_file.split('.txt')[0]+'.result'
#    get_frequent_features(input_file,output_file)
#
#    jpype.shutdownJVM()
    import os
    startJvm()
    input_dir = './../data/sentDicts'
    input_files = os.listdir(input_dir)
    print type(input_files[0])
#    input_files = ['./../data/Apex_AD2600_Progressive-scan_DVD_player_NOUNS.txt',
#                   './../data/Diaper_Champ_NOUNS.txt',
#                   './../data/ipod_NOUNS.txt',
#                   './../data/Linksys_Router_NOUNS.txt',
#                   './../data/Nokia_6610_NOUNS.txt']

    for input_file in filter(lambda x: x.endswith('txt'), input_files):
        input_file = os.path.join(input_dir,input_file)
        print input_file
        output_file = input_file.split('.txt')[0]+'.result'
        get_frequent_features(input_file,output_file)
    jpype.shutdownJVM()
    pass

