from create_inverted_index import InvertedIndex
from run_query import QueryEngine
import os

CORPUS_ROOT = f'{os.getcwd()}/corpus_time_test'

# create an inverted index based on the documents in the corpus folder
index_creator = InvertedIndex(CORPUS_ROOT)

# example entry in inverted index: {term: [doc_freq, total_freq, postings_list]}
# where postings list: [[doc_id, weighted_freq], ...]
weighted_index = index_creator.calculate_weighted_index(method='tf_idf')

# also need the document mapping: {doc_id : [doc_name (artist/song), doc_vector_length]}
# the document vector lengths will be helpful when running queries and calculating similiarities
doc_map = index_creator.calculate_document_vector_lengths()

# save the indexes as json so that they can be used seperately
index_creator.export_weighted_index('time_test_tfxidf_weighted_index.json')
index_creator.export_inverted_index('time_test_raw_count_index.json')
index_creator.export_document_mapping('time_test_document_mapping.json')

# initialize the query engine with the desired inverted index and document mapping
query_engine = QueryEngine('time_test_tfxidf_weighted_index.json', 'time_test_document_mapping.json')

# get the relevance results for each query that Time as specified
# store in a dictionary for easy lookup
with open("test_data/TIME.REL") as rel_f:
    relevance_dict = {} # {query_id: [list of doc_id]}
    for line in rel_f:
        try:
            split = line.split()
            relevance_dict[split[0]] = [doc_id for doc_id in split[1:]]
        except:
            pass

# run each query through the system and get back the top 10 results
# compare our results with Time's ground truth
evaluation_results = {} # {query_id: num_matches / total_relavent_documents}
with open("test_data/TIME.QUE") as query_f:
    # need to get the first query outside the loop
    first_line = query_f.readline()
    query_id = first_line.split()[-1]
    query_content = ''

    for line in query_f:
        if line.startswith('*FIND'):
            query_result = query_engine.query(query_content, num_results=10, print_results=False)
            doc_ids_returned = [result[0] for result in query_result]

            # check how many of the documents that Time specified for the query are actually returned by our system
            # score will just be matches / total relevant documents
            doc_ids_relavent = relevance_dict[query_id]
            matches = set(doc_ids_returned).intersection(set(doc_ids_relavent))
            score = len(matches) / len(doc_ids_relavent)
            evaluation_results[query_id] = score

            query_id = line.split()[-1]
            query_content = ''

        elif line.startswith('*STOP'):
            query_result = query_engine.query(query_content, num_results=10)
            doc_ids_returned = [result[0] for result in query_result]

            # check how many of the documents that Time specified for the query are actually returned by our system
            # score will just be matches / total relevant documents
            doc_ids_relavent = relevance_dict[query_id]
            matches = set(doc_ids_returned).intersection(set(doc_ids_relavent))
            score = len(matches) / len(doc_ids_relavent)
            evaluation_results[query_id] = score

        else:
            query_content += line 

# print out results and average the scores
format_template = "{:10}| {:10}"
print(format_template.format('Query', 'Score'))
print('='*30)
total = 0
for query_id, score in evaluation_results.items():
    total += score
    print(format_template.format(query_id, score))

print(f'Average Score: {total/len(evaluation_results)}')
