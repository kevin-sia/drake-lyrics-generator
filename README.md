# Lyrics Generator

The aim of this project is to create a lyrics generator for any artist's lyrics, with the original intent being a Drake lyrics generator.  It is comprised of two major parts:

1. Code for scraping lyrics and generating a lyrics file for a single artist
2. Code for lyrics generation, via a recurrent neural network (RNN)

---

## 1. Lyrics Scraping

Lyrics are collected using the `scrape_artist_lyrics.py` Python script, then merged into a single file using the `concatenate.sh` shell script.

`scrape_artist_lyrics.py`
- Takes in an AZLyrics artist page URL as user input, creates a directory for the artist, then scrapes all of the artist's lyrics from [AZLyrics](https://www.azlyrics.com/), putting each song's lyrics into its own text file in the directory that was created
- **Required packages:**
	- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)**
- Script is designed so that if the scraping must be interrupted, the individual song lyrics files that have already been obtained will remain

`concatenate.sh`
- Takes in the artist directory name as an argument, then concatenates each separate song lyrics file from that artist into a single lyrics file that is then placed in the `data` directory

`scrape_artist_lyrics.ipynb`
- Jupyter Notebook used to help develop the scraping script

---

## 2. Lyrics Generator

`text_generation_rnn_char.ipynb`
- A Jupyter Notebook in which a RNN is built, trained, and used to generate lyrics via *character prediction*
- **Required packages:**
	- **NumPy**
	- **TensorFlow 2.2**
- A good portion of the notebook is spent on setting up the lyrics into a format useable for a RNN

`text_generation_rnn_word.ipynb`
- Same as above, but for *word prediction*

---

## Notes
- The RNN built here is based on the [Text generation with an RNN tutorial](https://www.tensorflow.org/tutorials/text/text_generation) on the TensorFlow website
- Because RNNs learn from the *sequence* of the data, there may be a slight bit of mis-learning(?) during model training due to the structure of the provided lyrics data not being entirely sequential.  The single text file that the model trains on contains *all* of an artist's lyrics, where the songs are ordered first by album release date and then by track order on each album.  Also, lyrics to any singles (i.e. songs released by themselves) are at the very end of the file (per the AZLyrics website design).  So, one aspect of the sequence that the model might learn is that between the end of one song and the start of another song, which in reality wouldn't have very much meaning (unless the songs are part of a concept album?)
- There is a choice between using *character vectorization* vs. *word vectorization* - character vectorization might be more useful when there is less lyrics data, but word vectorization should result in more meaningful generated lyrics.  Regardless, it is probably best to train the generator on a large body of lyrics
- Note that the data will include lyrics from guest features.  If we wanted to make a Drake lyrics generator, the writing style of a guest might impart different patterns than Drake's.  However, I wouldn't imagine that guest verses are too prevalent in a corpus of lyrics

---

## Next Steps

- Play with the neural network architecture (sizes, recurrent layer types) to see how that changes the predictions/generations
- Transfer the Jupyter Notebooks into Python scripts