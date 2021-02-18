import requests
import re
from bs4 import BeautifulSoup
import os
import time
from string import ascii_lowercase, digits, punctuation
import random



# helper function for formatting song file names into song url names (retain only digits and lowercase letters)
def song_name_for_url(song_name):
    
    # make song name lowercase
    song_name = song_name.lower()
    
    # empty string to append characters to
    song_name_url = str()
    
    # loop through each character of the song name
    for char in song_name:
        
        # if the character is either a lowercase letter or a digit,
        if (char in ascii_lowercase) or (char in digits):
            
            # append it to the new string
            song_name_url += char
            
    return song_name_url



### MAYBE USE A COMMAND LINE ARGUMENT FOR THE ARTIST NAME INSTEAD? ###
### THEN PUT THAT ARGUMENT DIRECTLY INTO AN AZLYRICS URL ###
### RETURN ERROR IF URL INVALID (DETERMINED VIA GET REQUEST?) ###

# input artist page from azlyrics
artist_url = input('\nPlease input an artist page URL from AZLyrics (e.g. https://www.azlyrics.com/d/drake.html).\nURL: ')

# check if valid azlyrics artist page URL
if re.match(pattern='https:\/\/www\.azlyrics\.com\/([a-z]|[1][9])\/.+\.html', string=artist_url):
    
    
    ### OBTAINING ARTIST NAME AND CREATING DIRECTORY FOR ARTIST'S LYRICS ###
    
    # send GET request
    r_songs = requests.get(artist_url)

    # beautify the request response
    soup_songs = BeautifulSoup(r_songs.content, features='html.parser')
    
    # obtain artist name
    artist_name = soup_songs.find_all('strong')[0].text[:-7]
    artist_dir_name = artist_name.lower().replace(' ', '_')
    print(f'\nObtaining lyrics from songs by {artist_name}.')
    
    # create directory to store lyrics in
    if not os.path.exists(f'lyrics/{artist_dir_name}'):
        os.mkdir(f'lyrics/{artist_dir_name}')
        print(f'\n"{artist_dir_name}" directory created in the lyrics directory.')

    # print message if it already exists
    else:
        print(f'\n"{artist_dir_name}" directory already exists in the lyrics directory.')
    
    
    
    ### OBTAINING SONG NAMES AND LYRICS PAGE URLs ###
    
    # empty lists to store href links and song names in
    page_urls = list()
    song_names = list()

    # parse through the 'a' elements and obtain the href links
    for link in soup_songs.find_all('a'):

        # href link
        href = link.get('href')

        # check if this href link is a string
        if isinstance(href, str):

            # if the string is a valid lyrics page URL (kind of hack-y/hard-coded method here)
            if link.get('href')[:9] == '../lyrics':

                # then append the href link to the page links list
                page_urls.append(link.get('href'))

                # get song name
                song_name = link.text

                # append song name to list
                song_names.append(song_name)

    # remove duplicates from both links and song name lists, and sort them
    page_urls = list(dict.fromkeys(page_urls))
    song_names = list(dict.fromkeys(song_names))

    # recreate the song names list but convert each name into formats useable for URLs
    song_url_names = list()
    for song_name in song_names:
        song_url_names.append(song_name_for_url(song_name))
    
    # empty list to store full lyrics page URLs in
    page_urls_complete = []

    # loop through each href link from the previous list
    for link in page_urls:

        # attach the azlyrics URL to the rest of the link
        page_urls_complete.append('https://www.azlyrics.com' + link[2:])

    # number of songs recognized
    num_songs = len(song_names)

    # completion message for URL retrieval
    print(f'\nRetrieval of URLs is complete.  {num_songs} songs recognized.')
    
    
    
    ### SCRAPING LYRICS ###
    
    # set timer between API quests
    sleep_timer_min = 18
    sleep_timer_max = 22

    # print(f'Sleep timer between API requests is set to {sleep_timer} seconds.')
    print(f'Lyrics scraping will take {round(num_songs*sleep_timer_max/60, 1)} minutes at most.\n')

    # create empty list for song names whose lyrics can't be saved (in the `except` statement below)
    log = list()

    # error counter
    error_counter = 0

    # loop through every song
    for i in range(len(song_names)):

    	### RANDOMIZE THE SLEEP TIMER (SOME KIND OF UPPER AND LOWER BOUNDS?) WITHIN THE LOOP??? ###

        # create a potential lyrics file name
        lyrics_file_name = f'lyrics/{artist_dir_name}/{song_url_names[i]}.txt'

        # if the lyrics file already exists,
        if os.path.exists(lyrics_file_name):

            # print a message saying that it already exists in the artist director
            print(f'Lyrics for "{song_names[i]}" already exist at lyrics/{artist_dir_name}/{song_url_names[i]}.txt.')

        # if the lyrics file DOESN'T exist,
        else:

            # loop through every lyrics page URL
            for url in page_urls_complete:

                # check if the song URL name is in the lyrics page URL
                if song_url_names[i] in url:

                    # send GET request
                    r_lyrics = requests.get(url)

                    # beautify the request response
                    soup_lyrics = BeautifulSoup(r_lyrics.content, features='html.parser')

                    # find all div elements
                    divs = soup_lyrics.find_all('div')

                    # found by trial and error - lyrics are located at the 21st element (index 20) of the list returned by
                    # the .find_all('div') method on each azlyrics lyrics page (this is kind of hack-y and non-robust... oops)
                    lyrics = divs[20].text

                    # remove any square brackets (which, on azlyrics, indicate which person is singing/rapping/talking)
                    lyrics = re.sub('\[.*\]', '', lyrics)

                    # remove line breaks from beginning of lyrics
                    while lyrics[0] == '\n' or lyrics[0] == '\r':
                        lyrics = lyrics[1:]

                    # replace triple line breaks with double line breaks until there are no remaining triple line breaks
                    while '\n\n\n' in lyrics:
                        lyrics = lyrics.replace('\n\n\n', '\n\n')

                    # remove line breaks from end of lyrics
                    while lyrics[-1] == '\n' or lyrics[-1] == '\r':
                        lyrics = lyrics[:-1]

                    # attach triple line break to end of text to indicate end of song
                    lyrics_cleaned = lyrics + '\n\n\n'

                    # open/create an empty text file
                    with open(lyrics_file_name, 'w') as lyrics_file:

                        # adding this exception for when characters cannot be encoded
                        # e.g. the prime symbol in https://www.azlyrics.com/lyrics/drake/roundofapplause.html
                        try:

                            # write cleaned lyrics into a text file in the artist directory
                            lyrics_file.write(lyrics_cleaned)

                            # completion message for saving of song's lyrics to a text file
                            print(f'Lyrics for "{song_names[i]}" saved to {lyrics_file_name}.')

                        except UnicodeEncodeError:
                            
                            error_counter += 1

                            # message if text file can't be saved
                            print(f'Lyrics for "{song_names[i]}"" unable to be written (e.g. encoding issues).  {lyrics_file_name} saved as an empty text file.')
                            
                            # append song name to log list
                            log.append(song_names[i])
            
            # add sleep timer to prevent spamming GET requests
            time.sleep(random.randint(sleep_timer_min, sleep_timer_max))
    
    # create log file text
    log_str = f'Lyrics for the following {artist_name} songs were unable to be written:\n'
    for song in log:
        log_str += f'- {song}\n'
    
#    # write log file
#    log_file_name = f'{artist_dir_name}/__SCRAPING_LOG.txt'
#    with open(log_file_name, 'w') as log_file:
#        log_file.write(log_str)

    # summary statement
    print(f'\nLyrics for {len(song_names) - error_counter} songs have been saved to the lyrics/{artist_dir_name} directory.\n\n')

    # if any song lyrics were unable to be saved,
    if error_counter > 0:

        # print out what those songs are
        print(log_str)
    

# if input URL is not a valid AZLyrics artist page
else:
    
    print('Please input a valid artist page URL from AZLyrics (e.g. https://www.azlyrics.com/d/drake.html).\n')