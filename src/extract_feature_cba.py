import csv
import jpype
def preprocess_file(input_file,output_file):
    cin = open(input_file)
    itemsets = [line.split() for line in cin.readlines()]
    cin.close()
    word_set = list(set(reduce(lambda x,y:x+y,itemsets)))
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
                  "-Djava.class.path=%s/weka.jar" % (lib_home))

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
                for itemset in associator.__getattribute__('m_Ls')]
    import re
    def string2words(s):
        return ' '.join(re.findall(r'([\w\.-]+)=',s))

    return [map(string2words, itemset) for itemset in itemsets_vector]

def get_frequent_features(input_file,output_file): #TODO pruning
    csv_file = './../data/intermediate.csv'
    preprocess_file(input_file,csv_file)
    instances = get_instances(csv_file)
    itemsets = apriori(instances)
    jpype.shutdownJVM()
    return itemsets

if __name__=='__main__':
    input_file = './../data/data'
    output_file = './../data/test.csv'
#    preprocess_file(input_file,output_file)
    get_frequent_features(input_file,output_file)
    
    pass

