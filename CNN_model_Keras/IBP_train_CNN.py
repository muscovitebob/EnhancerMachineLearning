'''
Created on 12 Nov 2018

@author: wimth
'''
import numpy as np
import os
import pickle

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder       
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv1D, MaxPooling1D
from keras.callbacks import ModelCheckpoint, EarlyStopping,TensorBoard
from keras.utils import plot_model


WORK_DIR = r'E:\Downloads\IBP_project\Deep_learing_model'
#FILE_INPUT = 'train_toy_100recs.fna'
FILE_INPUT = 'deep_learning_train_chr2.fna'

SAVE_PICKLE_DATA=True
LOAD_PICKLE_DATA=False

BATCH_SIZE = 100
EPOCHS = 10


l_keys = ['train_seq','train_label','names','onehot_train_seq','onehot_train_label']


def parse_fasta_into_dict():
    l_sequences = []
    l_labels= []
    l_names =[]
    d_CNN_matrix = {}
    
    with open(os.path.join(WORK_DIR,FILE_INPUT)) as f: 
        for line in f: 
            line=line.rstrip()
            if line.startswith('>'):
                l_labels.append(line[-1:])
                l_names.append(line[1:-2])
            else:
                l_sequences.append(line.upper())
                
                
    d_CNN_matrix [l_keys[0]]=l_sequences
    d_CNN_matrix [l_keys[1]]=l_labels
    d_CNN_matrix [l_keys[2]]=l_names
    
    return d_CNN_matrix

def encode_seq_onehot(a_seq,a_labels):
    def encode_1hot_single_row(input_string):
        integer_encoded = label_encoder.fit_transform(np.array(list(input_string))) #will give numeric values, alphabetically, so encoding will be similar for all sequences (A=0, C=1, G=2, T=3)
        integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
        onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
        if onehot_encoded.shape[1]==5 and 'N' in input_string:  #some sequences contain 'N', this will be the fourth column(only 18 present in trainingset) => cut the 'N'-column, the 'N's will be encoded with all zeros
            onehot_encoded = np.delete(onehot_encoded,3,axis=1)
        return onehot_encoded
    
    a_onehot_seq = np.zeros((len(a_seq),len(a_seq[0]),4))
    label_encoder = LabelEncoder()
    onehot_encoder = OneHotEncoder(sparse=False)
    for i in range(0,a_onehot_seq.shape[0]):
        a_onehot_seq[i,...]=encode_1hot_single_row(a_seq[i])
    
    a_onehot_label = encode_1hot_single_row(a_labels)
    return a_onehot_seq,a_onehot_label


    
#MAIN---------------------------------------------------------------

#load the data
print('#loading the data')
if LOAD_PICKLE_DATA:
    d_train_matrix = pickle.load(open(os.path.join(WORK_DIR,'traindata.pickle'), "rb"))
else:
    d_train_matrix = parse_fasta_into_dict()
    a_sequences= np.array(d_train_matrix['train_seq'])
    a_labels = np.array(d_train_matrix['train_label'])
    
    #a_labels[1:20]= 'I' #temp!!
    
    # turn into 1 hot
    print('#turning into 1hot')
    a_onehot_seq,a_onehot_label = encode_seq_onehot(a_sequences,a_labels)
    d_train_matrix[l_keys[3]]=a_onehot_seq
    d_train_matrix[l_keys[4]]=a_onehot_label
    
    if SAVE_PICKLE_DATA:
        print('d_train_matrix.__sizeof__=',d_train_matrix.__sizeof__())
        pickle.dump(d_train_matrix, open(os.path.join(WORK_DIR,'traindata.pickle'), "wb"))  
        print('pickle saved')
        
print(a_onehot_seq.shape, a_onehot_label.shape)
print('d_train_matrix.__sizeof__=',d_train_matrix.__sizeof__())

#building model
print('#building the model')
model = Sequential()
model.add(Conv1D(activation="relu",    #the output shape of this will be (815-(26-1),320)
                 input_shape=(a_onehot_seq.shape[1], 4), 
                 filters=320, 
                 kernel_size=26, 
                 strides=1, 
                 padding="valid"))


model.add(MaxPooling1D(pool_size=13, strides=13)) #the output shape of this will be ((815-(26-1))/13,320)
model.add(Dropout(0.3))

model.add(Flatten())
model.add(Dense(500,activation='relu'))

#model.add(Dense(input_dim=925, output_dim=2))
model.add(Dense(2,activation='softmax'))

print ('compiling model')
model.compile(loss='binary_crossentropy', 
              optimizer='rmsprop',
              metrics=['accuracy'])
#plotting model
plot_model(model, to_file=os.path.join(WORK_DIR,'IBP_model.png'))
print(model.summary())


#training the model
callbacks_list = [
    ModelCheckpoint(filepath=os.path.join(WORK_DIR,'best_model.{epoch:02d}-{val_loss:.2f}.h5'),
                                    monitor='val_loss',
                                    mode='min', 
                                    save_best_only=True),
    EarlyStopping(monitor='acc', patience=5,verbose=1),
    TensorBoard(log_dir=os.path.join(WORK_DIR,'./logs'))
]
# checkpointer = ModelCheckpoint(filepath=os.path.join(WORK_DIR,"WT_bestmodel.hdf5"), verbose=1, save_best_only=True)
# earlystopper = EarlyStopping(monitor='acc', patience=5, verbose=1)

model.fit(a_onehot_seq, 
          a_onehot_label, 
          batch_size=BATCH_SIZE, 
          epochs=EPOCHS, 
          validation_split=0.2,
          callbacks=callbacks_list,
          verbose=1)

#tresults = model.evaluate(np.transpose(testmat['testxdata'],axes=(0,2,1)), testmat['testdata'],show_accuracy=True)

#print tresults