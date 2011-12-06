sent_file = open("SentiWordNet_3.0.0_20100908.txt", 'r')

#make dicts

a_dict = {}
n_dict = {}
v_dict = {}
r_dict = {}

for line in sent_file:
    parts = line.split('\t')
    if(parts[0] == 'n'):
        for w in parts[4].split():
            save = w.split('#')
            n_dict[save[0]] = ([parts[2], parts[3]])

    if(parts[0] == 'v'):
        for w in parts[4].split():
            save = w.split('#')
            v_dict[save[0]] = ([parts[2], parts[3]])

    if(parts[0] == 'a'):
        for w in parts[4].split():
            save = w.split('#')
            a_dict[save[0]] = ([parts[2], parts[3]])

    if(parts[0] == 'r'):
        for w in parts[4].split():
            save = w.split('#')
            r_dict[save[0]] = ([parts[2], parts[3]])

vocab = open('vocab.txt', 'r')
results = open('senti_results.txt', 'w')

for line in vocab:
    line = line.lower()
    line = line.strip()
    res = line
    if(line in n_dict.keys()):
        res = res + ' ' +  str(n_dict[line])
    else: res = res + ' ' + str(['0','0'])
    if(line in a_dict.keys()):
        res = res + ' ' + str(a_dict[line])
    else: res = res + ' ' + str(['0','0'])
    if(line in r_dict.keys()):
        res = res + ' ' + str(r_dict[line])
    else: res = res + ' ' + str(['0','0'])
    if(line in v_dict.keys()):
        res = res + ' ' + str(v_dict[line])
    else: res = res + ' ' + str(['0','0'])
    results.write(res + '\n')
    results.flush()
                          

