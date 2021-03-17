from genius_api import GeniusApi
from create_inverted_index import InvertedIndex
from run_query import QueryEngine
import os

artists = [
        '50 Cent',
        'Action Bronson',
        'Andre 3000',
        'ASAP Rocky',
        'Bas',
        'Big L',
        'Big Sean',
        'Cardi B',
        'Chance the Rapper',
        'Childish Gambino',
        'Common',
        'Drake',
        'Earl Sweatshirt',
        'Eminem',
        'G-Eazy',
        'Ghostface Killah',
        'Isaiah Rashad',
        'J Cole',
        'Jay-Z',
        'Joey Badass',
        'Kanye West',
        'Kendrick Lamar',
        'Kid Cudi',
        'Lil Wayne',
        'Logic',
        'Mac Miller',
        'Meek Mill',
        'MF Doom',
        'Nas',
        'Nicki Minaj',
        'NWA',        
        'Pusha-T',
        'Rick Ross',
        'Schoolboy Q',
        'Snoop Dogg',
        'Tech N9ne',
        'The Notorious BIG',
        'Travis Scott',
        'Tupac Shakur',
        'Tyler the Creator',
        'Wiz Khalifa'
    ]

SCRAPE_GENIUS = False
NUM_SONGS = 30
CORPUS_ROOT = f'{os.getcwd()}/corpus_songs'

if SCRAPE_GENIUS:
    # scrape the lyric data from genius.com and each song as seperate documents under the corpus folder
    access_token = 'SUPPLY ACCESS TOKEN HERE'
    genius = GeniusApi(access_token)

    # will try to get 30 songs from each artist
    # though most will have less because the API returns all songs the artist has been a part of
    # we only want the songs that the artist is the primary artist on though
    genius.get_songs_for_all_artists(artists, num_songs=NUM_SONGS, out_folder='corpus_songs')

# create an inverted index based on the documents in the corpus folder
index_creator = InvertedIndex(CORPUS_ROOT)

# example entry in inverted index: {term: [doc_freq, total_freq, postings_list]}
# where postings list: [[doc_id, weighted_freq], ...]
weighted_index = index_creator.calculate_weighted_index(method='tf_idf')

# also need the document mapping: {doc_id : [doc_name (artist/song), doc_vector_length]}
# the document vector lengths will be helpful when running queries and calculating similiarities
doc_map = index_creator.calculate_document_vector_lengths()

# save the indexes as json so that they can be used seperately
index_creator.export_weighted_index('rap_tfxidf_weighted_index.json')
index_creator.export_inverted_index('rap_raw_count_index.json')
index_creator.export_document_mapping('rap_document_mapping.json')

# initialize the query engine with the desired inverted index and document mapping
query_engine = QueryEngine('rap_tfxidf_weighted_index.json', 'rap_document_mapping.json')

# make some queries and print out the results
results = query_engine.query('cars money dollars quarters', num_results=10, print_results='rap_lyrics')
results = query_engine.query('medicine doctor nurse hospital', num_results=10, print_results='rap_lyrics')
results = query_engine.query('kunta king lamar kendrick', num_results=10, print_results='rap_lyrics')
results = query_engine.query('drunk drink alcohol', num_results=10, print_results='rap_lyrics')
