import tensorflow as tf
from string import punctuation
import numpy as np
import os
import time
import pickle

# create directory to store pickled files in
if not os.path.exists(f'pkl'):
    os.mkdir(f'pkl')

# ----------------------------------------------------------------------

### LIMITING GPU MEMORY GROWTH ###

# get list of visible GPUs
gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus: # if GPU(s) is detected
    try: # try setting memory growth to true for all GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True) # enabling memory growth
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print('\n', len(gpus), 'Physical GPUs,', len(logical_gpus), 'Logical GPU')
    except RuntimeError as e:
        # memory growth must be set before GPUs have been initialized
        print('\n', e)

# ----------------------------------------------------------------------

### READ IN AND CLEAN THE LYRICS DATA ###

# ******TAKE IN USER INPUT FOR LYRICS (ARTIST NAME? FILE NAME?)******

# read in the lyrics text file
text = str(open('data/drake_lyrics.txt', 'r').read())
# artist_name = input('\nPlease ')

# make all letters lowercase and make line breaks into its own "word"
words = text.lower().replace('\n', ' \n ')

# remove punctuation
for punc in punctuation:
	words = words.replace(punc, '')

# split the entire words string into a Python list of words
words = words.split(' ')

# obtain list of unique words across all lyrics
vocab = sorted(set(words))
print(f'\nThere are {len(vocab)} unique words in the lyrics file.')

# pickle the vocab file - will need it for the generation script
outfile = open(file='pkl/vocab', mode='wb')
pickle.dump(vocab, outfile)
outfile.close()

# ----------------------------------------------------------------------

### WORD MAPPING ###

# map unique characters to indices
word2idx = {u:i for i, u in enumerate(vocab)}

# pickle this since it is needed in text generation
outfile = open(file='pkl/word2idx', mode='wb')
pickle.dump(word2idx, outfile)
outfile.close()

# reverse the map - use this to specify an index to obtain a character
idx2word = np.array(vocab)

# pickle this since it is needed in text generation
outfile = open(file='pkl/idx2word', mode='wb')
pickle.dump(idx2word, outfile)
outfile.close()

# entire text document represented in the above character-to-indices mapping
words_as_int = np.array([word2idx[c] for c in words])

# ----------------------------------------------------------------------

### CREATING TRAINING EXAMPLES & TARGETS ###

# ******TAKE IN USER INPUT FOR SEQUENCE LENGTH?******

# max sentence length (in number of words) desired for training
seq_length = 100
# seq_length = input('\nPlease enter a desired sequence length (in number of words) to train the model on: ')
examples_per_epoch = len(words) // (seq_length + 1) # floored division

# create training examples/targets
word_dataset = tf.data.Dataset.from_tensor_slices(words_as_int)

# data type of train examples/targets
print('\n', type(word_dataset))

# create sequence batches from the word_dataset
sequences = word_dataset.batch(seq_length + 1, drop_remainder=True)
print('\n', type(sequences))

# define the shifting (splitting) function
def split_input_target(chunk):
    input_text = chunk[:-1] # up to but not including the last character
    target_text = chunk[1:] # everything except for the firs tcharacter
    return input_text, target_text

# apply the shifting to create input texts and target texts that comprise of our dataset
dataset = sequences.map(split_input_target)

# ----------------------------------------------------------------------

### CREATE TRAINING BATCHES ###

# batch size
BATCH_SIZE = 64

# buffer size to shuffle the dataset
# (TensorFlow data is designed to work with possibly infinite sequences,
# so it doesn't attempt to shuffle the entire sequence in memory.  Instead,
# it maintains a buffer in which it shuffles elements)
BUFFER_SIZE = 10000

# create a dataset that has been shuffled and batched
dataset_sb = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

# display batch dataset shapes and data types
print('\n', dataset_sb)

# ----------------------------------------------------------------------

### BUILDING THE RNN ###

# vocabulary length (number of unique words in dataset)
vocab_size = len(vocab)

# embedding dimension
embedding_dim = 256

# number of RNN units
rnn_units = 1024

# pickle model parameters - will need in the generation script
model_params = [vocab_size, embedding_dim, rnn_units]
outfile = open(file='pkl/model_params', mode='wb')
pickle.dump(model_params, outfile)
outfile.close()

# helper function to quickly build the RNN model based on vocab size, embedding dimension, number of RNN units, and batch size
def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
	
	# initialize sequential model architecture
    model = tf.keras.Sequential()
    
    # add embedding layer
    model.add(tf.keras.layers.Embedding(
        input_dim = vocab_size,
        output_dim = embedding_dim,
        batch_input_shape=[batch_size, None]
    ))
    
    # add recurrent layer
    model.add(tf.keras.layers.GRU(
        units = rnn_units,
        return_sequences = True,
        stateful = True,
        recurrent_initializer = 'glorot_uniform'
    ))

    # add dense layer
    model.add(tf.keras.layers.Dense(units=vocab_size))
    
    return model

# build the model using the above helper function
rnn = build_model(
    vocab_size = vocab_size,
    embedding_dim = embedding_dim,
    rnn_units = rnn_units,
    batch_size = BATCH_SIZE
)

# check the shape of the output
for input_example_batch, target_example_batch in dataset_sb.take(1):
    example_batch_predictions = rnn(input_example_batch)
    print('\n', example_batch_predictions.shape, '# (batch_size, sequence_length, vocab_size)')

# model architecture summary
print('\n', rnn.summary(), '\n')

# ----------------------------------------------------------------------

### SET UP METRICS ###

# helper function to obtain the loss function
def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

# compile the model
rnn.compile(
    optimizer = 'adam',
    loss = loss,
    metrics = ['accuracy']
)

# create directory where the checkpoints will be saved
checkpoint_dir = './training_checkpoints'

# name of the checkpoint files
checkpoint_prefix = os.path.join(checkpoint_dir, 'checkpoint')

# create checkpoints-saving object
checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath = checkpoint_prefix,
    monitor = 'loss',
    save_best_only = True,
    mode = 'min',
    save_weights_only = True
)

# ----------------------------------------------------------------------

### MODEL TRAINING ###

# set number of desired epochs
EPOCHS = 5

# training!
history = rnn.fit(
    x = dataset_sb,
    epochs = EPOCHS,
    callbacks = [checkpoint_callback]
)