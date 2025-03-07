import numpy as np

sg_text = open('/users/august.warren/documents/sg_descriptions.txt', encoding='utf8').read()

corpus_text = sg_text.split()

def make_pairs(corpus):
    for i in range(len(corpus)-1):
        yield (corpus[i], corpus[i+1])
        
pairs = make_pairs(corpus_text)

word_dict = {}

for word_1, word_2 in pairs:
    if word_1 in word_dict.keys():
        word_dict[word_1].append(word_2)
    else:
        word_dict[word_1] = [word_2]
 
first_word = np.random.choice(corpus_text)

while first_word.islower():
    first_word = np.random.choice(corpus_text)

chain = [first_word]
def hc_generator(corpus,length):
    first_word = np.random.choice(corpus)
    while first_word.islower():
        first_word = np.random.choice(corpus)
    chain = [first_word]
    n_words = length
    for i in range(n_words):
        chain.append(np.random.choice(word_dict[chain[-1]]))
    return(' '.join(chain))

print(hc_generator(corpus_text,15))
