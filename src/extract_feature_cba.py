import csv
def preprocess_file(input_file,output_file):
    cin = open(input_file)
    itemsets = [line.split() for line in cin.readlines()]
    cin.close()
    print reduce(lambda x,y:x+y,itemsets)
    word_set = list(set(reduce(lambda x,y:x+y,itemsets)))
    word_dict = dict([(w,i) for i,w in enumerate(word_set)])
    item_map = [[word_dict[w] for w in line] for line in itemsets]

    cout = open(output_file,'wb')
    csvWriter = csv.writer(cout,delimiter=' ',
                           quotechar='|',quoting=csv.QUOTE_MINIMAL)
    csvWriter.writerow(word_set)
    for item in item_map:
        line = ['?']*len(word_set)
        def trans_mark(i):
            line[i]='yes'
        map(trans_mark,item)
        csvWriter.writerow(line)
    cout.close()

if __name__=='__main__':
    input_file = 'data'
    output_file = 'test.csv'
    preprocess_file(input_file,output_file)
    
    pass

