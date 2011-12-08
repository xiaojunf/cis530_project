import csv
import jpype
import nltk

word_sent_dict = nltk.defaultdict(set)

def preprocess_file(input_file,output_file):
    cin = open(input_file)
    itemsets = [line.split() for line in cin.readlines()]
    cin.close()


#    global word_sent_dict
#    word_sent_dict = nltk.defaultdict(set)
    def add2dict((idx,words)):
        map(lambda x: word_sent_dict[x].add(idx), words)
    map(add2dict,enumerate(itemsets))

    word_set = list(set(reduce(lambda x,y:x+y,itemsets)))
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

startJvm() # one jvm per python instance.

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
                for itemset in associator.__getattribute__('m_Ls')][:3]
    import re
    def string2words(s):
        return ' '.join(re.findall(r'(\w+)=',s))

    return [map(string2words, itemset) for itemset in itemsets_vector]

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
    jpype.shutdownJVM()
    itemset_one = redundant_pruning(itemsets)
    import simplejson as json
    content = json.dumps({'itemset_1':itemset_one,
                         'itemset_2':itemsets[1],
                         'itemset_3':itemsets[2]})
    cout = open(output_file,'w')
    cout.write(content)
    cout.close()

if __name__=='__main__':
    input_file = './../data/data'
    output_file = './../data/result'
#    preprocess_file(input_file,output_file)
    get_frequent_features(input_file,output_file)
    
    pass

