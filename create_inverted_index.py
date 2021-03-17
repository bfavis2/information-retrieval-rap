import string
import nltk
import os
import json
import math
import copy

class InvertedIndex:
    """
    Class to create an inverted index given a folder path to a corpus where each file is treated as a seperate index
    """

    def __init__(self, corpus_root):
        self.corpus_root = corpus_root

        # documents are assumed to all be under the working-directory/corpus
        # each file is treated as a separate document
        # does NOT support subfolders in corpus directory right now
        for subdir, dirs, files in os.walk(self.corpus_root):
            self.documents = files
        self.total_docs = len(self.documents)

        self.stemmer = nltk.PorterStemmer()
        self.stop_words = nltk.corpus.stopwords.words('english')

        self.inverted_index = {}    # {term: [doc_freq, total_freq, postings_list]}
        self.doc_map = {}           # {doc_id : [artist/song, doc_vector_length]}
        self.weighted_index = {}    # same as inverted index except instead of raw count in postings, there are weighted frequencies

    def create_inverted_index(self):
        """
        Returns a inverted index with raw term counts as weights in the postings list
        """
        all_tokens = {}
        for i, filename in enumerate(self.documents):
            self.doc_map[i+1] = [filename.split('.')[0], 0]
            tokens = self.tokenize_document(filename)
            all_tokens[i+1] = tokens
            
        compiled_list = self.combine_document_tokens(all_tokens)
        self.inverted_index = self.merge_tokens(compiled_list)
        return self.inverted_index

    def tokenize_document(self, filename):
        """
        Helper method that proccesses a single document.
        Removes puncuation
        Tokenizes
        Removes stop words
        Removes non ascii words
        Performs stemming
        """
        token_dict = {}
        with open(self.corpus_root + '/' + filename, 'r', encoding='latin1') as f:
            for line in f:
                # remove puncuation
                line = line.translate(str.maketrans('', '', string.punctuation))
                words = [word.strip().lower() for word in line.split()]

                for word in words:
                    # get rid of the word if it has any non-ascii characters or it is a stop word
                    if word not in self.stop_words and all(ord(char) < 128 for char in word):
                        stem = self.stemmer.stem(word) # uses porter stemmer
                        if stem in token_dict:
                            token_dict[stem] += 1
                        else:
                            token_dict[stem] = 1

        return token_dict

    def combine_document_tokens(self, tokens_dict):
        """
        Compiles the information about each token
        """
        compiled_list = [] # contains entries of the form (term, doc_id, frequency_in_doc)
        for doc_id, tokens in tokens_dict.items():
            for term, freq in tokens.items():
                compiled_list.append((term, doc_id, freq))
        
        # sort the compiled list by term
        compiled_list.sort(key= lambda x: (x[0], x[1]))
        return compiled_list

    def merge_tokens(self, compiled_list):
        """
        Merges the token information together to create the inverted index
        """
        merged_dict = {} # example entry: {term: (doc_freq, total_freq, postings_list)}
        for term, doc_id, freq in compiled_list:
            if term in merged_dict:
                merged_dict[term][0] += 1
                merged_dict[term][1] += freq
                merged_dict[term][2].append([doc_id, freq])
                
            else:
                merged_dict[term] = [1, freq, [[doc_id, freq]]]
                
        return merged_dict

    def calculate_weighted_index(self, method='tf_idf'):
        """
        Weights the terms of the inverted index based on the selected method
        """
        # create the inverted index if it doesn't exist yet
        if not self.inverted_index:
            self.create_inverted_index()

        self.weighted_index = copy.deepcopy(self.inverted_index)
        if method == 'tf_idf':
            for term, values in self.weighted_index.items():
                doc_freq = values[0]
                total_freq = values[1]
                postings = values[2]

                idf = math.log(self.total_docs / doc_freq, 2)

                for posting in postings:
                    posting[1] *= idf
        
        return self.weighted_index

    def calculate_document_vector_lengths(self, inverted_index=None):
        """
        Calculates the norm of the doc vector based off the weights of a given inverted index
        """
        # use the weighted index by default
        if inverted_index == None:
            inverted_index = self.weighted_index

        # initialize the doc lengths for each document as 0
        for doc_index, values in self.doc_map.items():
            values[1] = 0

        # loop through all the postings list and keep a running sum of the squared weighted frequency for each document
        for term, values in inverted_index.items():
            postings = values[2]
            for doc_index, weight in postings:
                self.doc_map[doc_index][1] += weight**2

        # after all the weights are summed, take the square root for each document to get the final vector length
        for doc_index, values in self.doc_map.items():
            values[1] = math.sqrt(values[1])

        return self.doc_map

    def print_index(self):
        """
        Prints the inverted index in a more readable format showing the term, document frequency, total frequency and the postings list
        """
        format_template = "{:30}|{:^10}|{:^12}| {:30}"
        print(format_template.format('Term', 'Doc Freq', 'Total Freq', 'Postings List'))
        print('='*60)
        for k, v in self.inverted_index.items():
            postings_list = ' -> '.join([str(posting) for posting in v[2]])
            print(format_template.format(k, v[0], v[1], postings_list))

    def export_inverted_index(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.inverted_index, f)

    def export_weighted_index(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.weighted_index, f)

    def export_document_mapping(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.doc_map, f)

# for testing          
if __name__ == '__main__':         
    index = InvertedIndex(os.getcwd() + '/corpus')
    inverted_index = index.create_inverted_index()
    weighted_index = index.calculate_weighted_index()
    doc_map = index.calculate_document_vector_lengths()
    print(index.total_docs)
    index.print_index()
    index.export_inverted_index('inverted_index.json')
    index.export_document_mapping('doc_mapping.json')
    index.export_weighted_index('weighted_index.json')
    # print(len(index.inverted_index))
    # print(doc_map)