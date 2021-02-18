#!/bin/bash

# bash script to concatenate all individual lyrics files from a single artist
# into a master lyrics file for that artist

# first argument is the artist directory name whose lyrics to concatenate

# check if a file exists with the same desired master lyrics file name
if [ -e data/$1_lyrics.txt ]; then

    printf 'File %s already exists in the data directory.\n' $1_lyrics.txt

# if not, create the file and perform the concatenation
else 

    printf 'File %s does not exist in the data directory.\n' $1_lyrics.txt

    # create master lyrics file for artist
	touch data/$1_lyrics.txt

	printf 'Empty text file %s created in the data directory.\n' $1_lyrics.txt

	#printf 'Concatenating %s files...' ls $1 | wc -l

	# concatenate all files in artist's directory
	# cat $1/*.txt >> data/$1_lyrics.txt
	cd $1
	cat $(ls -tr) >> ../data/$1_lyrics.txt

	printf 'Individual lyrics files successfully concatenated to /data/%s.\n' $1_lyrics.txt

fi