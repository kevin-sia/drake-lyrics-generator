import tensorflow as tf
from string import punctuation
import pickle

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

# -------------------------------------------------------------------------

### MODEL BUILDING FUNCTION FROM TRAINING SCRIPT ###

# helper function to quickly build the RNN model based on vocab size, embedding dimension, number of RNN units, and batch size
def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential()
    
    model.add(tf.keras.layers.Embedding(
        input_dim = vocab_size,
        output_dim = embedding_dim,
        batch_input_shape=[batch_size, None]
    ))
    
    model.add(tf.keras.layers.GRU(
        units = rnn_units,
        return_sequences = True,
        stateful = True,
        recurrent_initializer = 'glorot_uniform'
    ))
    
    model.add(tf.keras.layers.Dense(units=vocab_size))
    
    return model

# -------------------------------------------------------------------------

### INITIATE MODEL AND LOAD IN WEIGHTS FROM CHECKPOINT ###

# unpickle the model parameters from the training script
infile = open(file='pkl/model_params', mode='rb')
vocab_size, embedding_dim, rnn_units = pickle.load(infile)
infile.close()

# initiate new model instance
rnn_cp = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)

# load saved weights from checkpoint into new model instance
rnn_cp.load_weights(tf.train.latest_checkpoint('./training_checkpoints'))

# build the model with a new input shape
rnn_cp.build(tf.TensorShape([1, None]))

# -------------------------------------------------------------------------

### TEXT PREDICTION FUNCTION ###

# unpickle the index-word files that were pickled from the training script
infile = open(file='pkl/word2idx', mode='rb')
word2idx = pickle.load(infile)
infile.close()
infile = open(file='pkl/idx2word', mode='rb')
idx2word = pickle.load(infile)
infile.close()

def generate_text(model, start_string, num_generate=500, temperature=1.0):
    
    # num of chars to generate
    num_generate = num_generate
    
    # vectorizing the start string to numbers
    input_eval = [word2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input=input_eval, axis=0) # returns a tensor with a length-1 axis inserted at index `axis`
    
    # empty string to store results
    text_generated = list()
    
    # "temperature"
    # low temperature results in more predictable text,
    # high temperature results in more surprising text.
    # feel free to experiment with this parameter
    temperature = 1.0
    
    # the batch size was defined when we loaded model weights from training
    
    model.reset_states()
    for i in range(num_generate):
        predictions = model(input_eval)
        
        # remove the batch dimension
        predictions = tf.squeeze(predictions, 0)
        
        # use a categorical distribution to predict the character returned by the model
        preidctions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()
        
        # pass the predicted character as the next input to the model along with the previous hidden state
        input_eval = tf.expand_dims([predicted_id], 0)
        
        text_generated.append(idx2word[predicted_id])
    
    return(' '.join(start_string + text_generated))

# -------------------------------------------------------------------------

### TAKE IN INPUT STRING AND CHECK IF ALL WORDS IN IT ARE IN THE VOCABULARY ###
# (this is a requirement for text generation)

# unpickle the vocabulary file that was pickled from the training script
infile = open(file='pkl/vocab', mode='rb')
vocab = pickle.load(infile)
infile.close()

# initialize the checking loop
check = True

while check:

	# take in user input for starting lyrics
	start_string = input('\nPlease input some text to initiate the lyrics generation (caps insensitive):\n')

	# lowercase
	start_string = start_string.lower()

	# remove punctuation
	for punc in punctuation:
		start_string = start_string.replace(punc, '')

	# create a list where each element is one word from the start string
	start_string = start_string.split(' ')

	# store all words that aren't in the vocabulary
	non_vocab = []

	# for every word in the start string
	for word in start_string:

		# if the word is NOT in the vocabulary
		if word not in vocab:

			# add the word to the non_vocab variable
			non_vocab.append(word)

	# if the non-vocab list is empty (i.e. all words in the start string are in the vocab)
	if non_vocab == []:

		# break out of the loop
		check = False

	# if there are words not in the vocabulary
	else:

		# print what those words are
		print(f'\nWords in the input text not present in the vocabulary are: {", ".join(non_vocab)}')
		print('\nAll input words must be in the vocabulary.')

# -------------------------------------------------------------------------

### TEXT GENERATION ###

# text generation!
print('\n', generate_text(rnn_cp, start_string=start_string, num_generate=250))

### SAVE TO FILE??? ###

# -------------------------------------------------------------------------

# -------------------------------------------------------------------------