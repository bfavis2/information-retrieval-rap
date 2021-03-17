# CSC575 Information Retrieval Project

Author: Brian Favis

Requirements:
- Python3
- BeautifulSoup
- requests
- nltk

In order to run queries with the prebuilt inverted index you will need to download:
- run_query.py
- *_tfxidf_weighted_index.json
- *_document_mapping.json

Then you can instatiate a QueryEngine class with the json files and use that to run queries.

`create_inverted_index.py` is used if you have a corpus and want to create your own inverted index.

`genius_api.py` is used if you want to create a corpus of rap lyrical data from genius.com.
