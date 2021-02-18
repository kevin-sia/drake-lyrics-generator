import requests
import re
from bs4 import BeautifulSoup
import os
import time
from string import punctuation

# input artist page from azlyrics
artist_url = input('\nPlease input an artist page from AZLyrics (e.g. https://www.azlyrics.com/d/drake.html).\n')

# check if valid azlyrics artist page URL
if re.match(pattern='https:\/\/www\.azlyrics\.com\/([a-z]|[1][9])\/.+\.html', string=artist_url):
    
    
    
    ### SCRAPING LYRICS PAGE URLs ###
    
    # send GET request
    r_songs = requests.get(artist_url)

    # beautify the request response
    soup_songs = BeautifulSoup(r_songs.content, features='html.parser')
    
    # obtain artist name
    artist_name = soup_songs.find_all('strong')[0].text[:-7]
    artist_path_name = artist_name.lower().replace(' ', '_').replace(',', '').replace('\'', '')
    print(f'\nObtaining lyrics from songs by {artist_name}.')
    
    # create directory to store lyrics in
    if not os.path.exists(artist_path_name):
        os.mkdir(artist_path_name)
        print(f'\n"{artist_path_name}" directory created in the working directory.')
    
    # print message if it already exists
    else:
        print(f'\n"{artist_path_name}" directory already exists in the working directory.')

    # empty list to store href links in
    page_links = []
    
    # parse through the 'a' elements and obtain the href links
    for link in soup_songs.find_all('a'):
        
        # href link
        href = link.get('href')
        
        # check if this href link is a string
        if isinstance(href, str):
            
            # if the string is a valid lyrics page URL (kind of hack-y/hard-coded method here)
            if link.get('href')[:9] == '../lyrics':
                
                # then append the href link to the page links list
                page_links.append(link.get('href'))

    # remove duplicates
    page_links = list(set(page_links))

    # empty list to store full lyrics page URLs in
    page_links_complete = []
    
    # loop through each href link from the previous list
    for link in page_links:
        
        # attach the azlyrics URL to the rest of the link
        page_links_complete.append('https://www.azlyrics.com' + link[2:])
    
    # sort the URLs for cleanliness
    # page_links_complete.sort()
    
    # number of songs obtained
    num_songs = len(page_links_complete)
    
    # completion message for URL retrieval
    print(f'\nRetrieval of URLs is complete.  {num_songs} songs obtained.')
    print(f'Sleep timer between API requests is set to 10 seconds.')
    print(f'Lyrics scraping will take {round(num_songs*10/60, 1)} minutes.\n')
    
    
    
    
    ### SCRAPING LYRICS ###
    
    # lyrics page URL
    for lyrics_page_url in page_links_complete:

        # send GET request
        r_lyrics = requests.get(lyrics_page_url)

        # beautify the request response
        soup_lyrics = BeautifulSoup(r_lyrics.content, features='html.parser')
        
        # obtain song name
        song_name = soup_lyrics.find_all('b')[1].text.replace('\"', '').replace('/', '')

        # create a song file name for file paths
        song_file_name = song_name.lower() # make lowercase
        for punc in punctuation:
            song_file_name = song_file_name.replace(punc, '') # delete all punctuation
        song_file_name = song_file_name.replace(' ', '_')

        # find all div elements
        divs = soup_lyrics.find_all('div')

        # found by trial and error - lyrics are located at the 21st element (index 20) of the list returned by
        # the .find_all('div') method on each azlyrics lyrics page
        lyrics = divs[20].text

        # remove any square brackets (which, on azlyrics, indicate which person is singing/rapping/talking)
        lyrics_cleaned = re.sub('\[.*\]', '', lyrics)

        # remove triple line breaks "\n\r\n" at the start of every file
        lyrics_cleaned = lyrics_cleaned.replace('\n\r\n', '')
        
        # file name/path for lyrics file
        lyrics_file_name = artist_name + '/' + song_file_name + '.txt'
        
        # write cleaned lyrics to a text file in the artist directory that was created
        if not os.path.exists(lyrics_file_name):
            with open(artist_path_name + '/' + song_file_name + '.txt', 'w') as lyrics_file:
                lyrics_file.write(lyrics_cleaned)
            
            # completion message for saving of song's lyrics to a text file
            print(f'Lyrics for {song_name} saved to the "{artist_path_name}" directory.')
            
        else:
            print(f'Lyrics for {song_name} already exist in the "{artist_path_name}" directory.')
        
        # sleep a bit to avoid spamming GET requests -- ***GOT RATE-LIMITED AT 2 SECOND SLEEP TIMER***
        time.sleep(10)
    
    # completion message
    print(f'\nAll song lyrics text files successfully saved to the {artist_name} directory.')
    
    

# if input URL is not a valid azlyrics artist page
else:
    print('\nPlease input a valid artist page from the AZLyrics website (e.g. https://www.azlyrics.com/d/drake.html).')