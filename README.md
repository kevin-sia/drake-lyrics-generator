# Lyrics Generator

![](https://images.ctfassets.net/cnu0m8re1exe/5shE8ddaU9AjSNz157nffI/eefd59783b225fc4b19f8bf10b640a4c/shutterstock_365531318.jpg?w=650&h=433)

The original intent of this project is to create a Drake lyrics generator, but future iterations may make this usable for any artist.  It is comprised of two major parts:

1. Lyrics scraping for a single artist
2. Lyrics generation

---

## 1. Lyrics Scraping

`scrape_artist_lyrics.py` - Scrapes all of an artist's lyrics from [AZLyrics](https://www.azlyrics.com/) and saves each song's lyrics to individual files in the `lyrics` directory.  Script is designed so that if the scraping must be interrupted, the individual song lyrics files that have already been obtained will remain, and when scraping is resumed for the same artist, it will begin where it left off.  **Required packages: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).**

`concatenate.sh` - Takes in the artist directory name as an argument, then concatenates each separate song lyrics file from that artist into a single lyrics file that is then placed in the `data` directory.

---

## 2. Lyrics Generator

`rnn_train.py` - Preprocesses text data and trains an RNN for text generation.  **Required packages: [NumPy](https://numpy.org/install/) and [TensorFlow 2.2](https://www.tensorflow.org/install).**

`rnn_generate.py` - Generates text based on the trained RNN.  **Required packages: [TensorFlow 2.2](https://www.tensorflow.org/install).**

---

## Notes
- Because RNNs learn from the *sequence* of the data, there may be a slight bit of mis-learning(?) during model training due to the structure of the provided lyrics data not being entirely sequential.  The single text file that the model trains on contains *all* of an artist's lyrics, where the songs are ordered first by album release date and then by track order on each album.  Also, lyrics to any singles (i.e. songs released by themselves) are at the very end of the file (per the AZLyrics website design).  So, one aspect of the sequence that the model might learn is that between the end of one song and the start of another song, which in reality wouldn't have very much meaning (unless the songs are part of a concept album?)
- There is a choice between using *character vectorization* vs. *word vectorization* - character vectorization might be more useful when there is less lyrics data, but word vectorization should result in more meaningful generated lyrics.  Regardless, it is probably best to train the generator on a large body of lyrics.  Currently, the training and generator scripts are based on *word prediction*
- Note that the data will include lyrics from guest features.  If we wanted to make a Drake lyrics generator, the writing style of a guest might impart different patterns than Drake's.  However, I wouldn't imagine that guest verses are too prevalent in a corpus of lyrics
- For sequence length 100, embedding dimension 256, RNN units 1024 and a GRU recurrent layer, generated text from a 5-epoch model (which ended in a 17.3% accuracy) seemed significantly more coherent than that from a 20-epoch model (which ended in a 33.6% accuracy)

---

## Next Steps

- Bypass lyrics file saving if there is an encoding issue with the characters
- Include estimated time of scraping completion?
- Play with model training parameters and maybe make them user-defined:
	- Sequence length
	- Embedding dimension
	- Recurrent layer types and sizes
	- Number of epochs
- Play with text generation parameters and maybe make them user-defined:
	- Temperature
- The input words for word generation must be present in the vocabulary that the model is trained on.  Include this in the generation script(s)