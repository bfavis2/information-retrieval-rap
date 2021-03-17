import json
import string
import nltk
import math

class QueryEngine:

    def __init__(self, inverted_index_json, doc_mapping_json):
        with open(inverted_index_json) as f:
            self.inverted_index = json.load(f)
        with open(doc_mapping_json) as f:
            self.doc_mapping = json.load(f)

        self.stemmer = nltk.PorterStemmer()
        self.stop_words = nltk.corpus.stopwords.words('english')

        self.query_raw = None
        self.query_processed = None
        self.query_length = None

        self.top_results = None

    def query(self, query, num_results=5, print_results='general'):
        """
        Returns the top n documents that the query is most similar to
        """
        similarity_scores = {doc_id:0 for doc_id in self.doc_mapping.keys()}
        self.query_raw = query
        self.query_processed = self.preprocess_query(self.query_raw)
        
        # calculate the similarity score for all terms and add them up
        for term in self.query_processed:
            sim_scores = self.calculate_similarity(term)
            for doc_id, score in sim_scores.items():
                similarity_scores[str(doc_id)] += score

        self.top_results = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)[:num_results]
        
        if print_results:
            self.print_results(method=print_results)
            
        return self.top_results
        
    def preprocess_query(self, query):
        """
        Proccesses the query so that it is easier to work with
        """
        query_processed = []
        query = query.translate(str.maketrans('', '', string.punctuation))
        words = [word.strip().lower() for word in query.split()]

        for word in words:
            # get rid of the word if it has any non-ascii characters or it is a stop word
            if word not in self.stop_words and all(ord(char) < 128 for char in word):
                stem = self.stemmer.stem(word) # uses porter stemmer
                query_processed.append(stem)

        # we are treating each query term with a weight of one
        # thus the length of the query vector would be the sqrt(num_terms)
        self.query_length = math.sqrt(len(query_processed))

        return query_processed

    def calculate_similarity(self, term, term_weight=1, method='cosine'):
        """
        Calculate the similarity score on a term basis
        """
        sim_scores = {} # {doc_id: similarity_score}
        
        if method == 'cosine':
            if term in self.inverted_index:
                postings = self.inverted_index[term][2]
                for posting in postings:
                    doc_id = posting[0]
                    weight = posting[1]
                    doc_length = self.doc_mapping[str(doc_id)][1]
                    score = (weight * term_weight) / (doc_length * self.query_length)
                    sim_scores[doc_id] = score

        return sim_scores

    def print_results(self, method='general'):
        if method == 'general':
            format_template = "{:10}|{:^25}| {:5}"
            print(format_template.format('Doc ID', 'Doc Name', 'Similarity Score'))
            print('='*60)
            for result in self.top_results:
                doc_id = result[0]
                score = result[1]
                doc_name = self.doc_mapping[str(doc_id)][0]

                if score != 0:
                    print(format_template.format(doc_id, doc_name, score))

        elif method == 'rap_lyrics':
            format_template = "{:45}|{:^25}| {:5}"
            print(format_template.format('Song', 'Artist', 'Similarity Score'))
            print('='*80)
            for result in self.top_results:
                doc_id = result[0]
                score = result[1]
                doc_name = self.doc_mapping[str(doc_id)][0]
                artist, song = doc_name.split('_', 1)

                if score != 0:
                    print(format_template.format(song, artist, score))
        return
