import requests
from bs4 import BeautifulSoup
import string
import os
import sys
import re

class GeniusApi:

    def __init__(self, access_token):
        self.base_url = 'https://api.genius.com'
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }
        self.script_path = os.path.dirname(os.path.realpath(__file__))
        return

    def get_songs_for_all_artists(self, artist_list, num_songs=20, sort='popularity', out_folder='songs'):
        """
        Loops through the artist list and gets the lyrics for n most popular songs
        """
        for artist in artist_list:
            self.get_artist_songs(artist, num_songs, sort, out_folder=out_folder)
        return

    def get_artist_songs(self, artist_name, num_songs=20, sort='popularity', out_folder='songs'):
        """
        Uses the Genius API to get the top n songs for an artist
        Then uses Beautiful Soup to scrape the lyric data off of genius.com website
        """
        artist_id = self.get_artist_id(artist_name)
        endpoint = f'/artists/{artist_id}/songs'
        params = {
            'sort': sort,
            'per_page': num_songs
        }
        r = requests.get(self.base_url + endpoint, params=params, headers=self.headers)

        # loop through the songs and extract the title and song id
        for song_details in r.json()['response']['songs']:
            # only retrieve the songs where the artist is the primary artist of the song
            if song_details['primary_artist']['id'] == artist_id:
                title = song_details['title']
                title = title.translate(str.maketrans('', '', string.punctuation)) # remove puncuation
                song_text = self.get_song_text(song_details['url'])
                self.create_lyric_file(artist_name, title, song_text, out_folder=out_folder)
        return

    def get_artist_id(self, artist_name):
        endpoint = '/search/'
        params = {
            'q': artist_name
        }
        r = requests.get(self.base_url + endpoint, params=params, headers=self.headers)
        artist_id = r.json()['response']['hits'][0]['result']['primary_artist']['id']
        return artist_id

    def get_song_text(self, url):
        lyric_page = requests.get(url)
        html = BeautifulSoup(lyric_page.text, 'html.parser')

        lyrics = html.find('div', class_='lyrics').get_text()
        lyrics = lyrics.encode('utf8', 'ignore').decode('utf8').strip()
        lyrics = re.sub('\[.*\]', '', lyrics)  # Remove [Verse] and [Bridge] stuff
        lyrics = re.sub('\n{2}', '\n', lyrics)  # Remove gaps between verses
        lyrics = str(lyrics).strip('\n')
        return lyrics

    def create_lyric_file(self, artist_name, song_title, song_text, filename='auto', out_folder='songs'):
        out_folder_path = os.path.join(self.script_path, out_folder)
        if filename == 'auto':
            filename = f'{artist_name}_{song_title}.txt'

        if not os.path.exists(out_folder_path):
            os.makedirs(out_folder_path)

        with open(os.path.join(out_folder_path, filename), 'wb') as f:
            f.write(song_text.encode('utf-8'))

        return