'''
Created on 7 Dec 2018

@author: wimth
'''
# X: one hot sequences
# model: trained model
# nsite_true_limit: how many top scored sequences you will use for generating pwm

import tensorflow as tf
import numpy as np
from keras.models import load_model
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder 


WORK_DIR = ''
FILE_NAME_MODEL_FROM_DISK = 'best_model.08-0.79_MODEL3.h5'
FILE_INPUT_TRAIN = 'deep_learning_cent_shuffled.fna'
SEQ_LENGTH = 815
BATCH_SIZE= 10000

def encode_1hot_single_sequence(input_string,label_encoder,onehot_encoder):
    integer_encoded = label_encoder.fit_transform(np.array(list(input_string))) #will give numeric values, alphabetically, so encoding will be similar for all sequences (A=0, C=1, G=2, T=3)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    if onehot_encoded.shape[1]==5 and 'N' in input_string:  #some sequences contain 'N', this will be the fourth column(only 18 present in trainingset) => cut the 'N'-column, the 'N's will be encoded with all zeros
        onehot_encoded = np.delete(onehot_encoded,3,axis=1)
    return onehot_encoded

def load_model_from_disk(file_name_model):
    
    print('#loading the model')
    model = load_model(os.path.join(WORK_DIR,file_name_model))
    print('model {0} is loaded'.format(file_name_model))
    
    return model

def handle_sequences(X):
    filter_manual_valid = tf.Session().run(tf.nn.conv1d(X.astype('float32'), weights, 1, padding='VALID'))
    print('after convolution')
    test_filter_manual = np.array(filter_manual_valid,copy=True)
    for motif in motif_numbers:
        sequence = []
        count = np.ones((motif_len,4))
        nsite_true = 4
        min_value=test_filter_manual[:,:,motif].min()
        while nsite_true<nsite_true_limit:
            region = int(test_filter_manual[:,:,motif].argmax() / (test_filter_manual.shape[1]))
            location = test_filter_manual[:,:,motif].argmax() % (test_filter_manual.shape[1])
            if (test_filter_manual[region,location,motif]==0):
                test_filter_manual[region,location,motif] = min_value 
                if np.sum(X[region,location:location+motif_len])==0:
                    test_filter_manual[region,:] = min_value
                continue
            count= count + X[region,location:location+motif_len]
            nsite_true = nsite_true + 1
            test_filter_manual[region,location,motif] = min_value  
            sequence.append(X[region,location:location+motif_len])
        #plot_weights(count/nsite_true)
        counts.append(count/nsite_true)
        nsites_true.append(nsite_true)
        sequences.append(sequence)
        print('sequence added ',str(len(sequences)))
    return sequences

def write_pswm(sequences):
    seq_agg=np.sum(sequences,axis=(1))/len(sequences[0])
    full_path = os.path.join(WORK_DIR,FILE_NAME_MODEL_FROM_DISK[:-3]+'.motif')
    with open(full_path, 'w',newline='') as f_out:  
        for ix_motif in range(0,seq_agg.shape[0]):
            f_out.write(">motif{0}{1}".format(ix_motif,'\n'))
            for ix_position in range(0,seq_agg.shape[1]):
                for ix_nucleotide in range(0,seq_agg.shape[2]):
                    f_out.write(str(seq_agg[ix_motif,ix_position,ix_nucleotide]))
                    if ix_nucleotide==3:pass
                    else:f_out.write("\t")
                f_out.write("\n")
    return
                    

model = load_model_from_disk(FILE_NAME_MODEL_FROM_DISK)
weights = model.get_weights()[0]


counts = []
sequences = []
nsites_true = []
nsite_true_limit = 100
motif_len = weights.shape[0]
motif_numbers = range(weights.shape[2])


f = open(os.path.join(WORK_DIR,FILE_INPUT_TRAIN))
a_onehot_seq = np.zeros((BATCH_SIZE,SEQ_LENGTH,4))
label_encoder = LabelEncoder()
onehot_encoder = OneHotEncoder(sparse=False)
ix_seq =0
for line in f:
    line=line.rstrip()
    if line.startswith('>'):continue
    else:
        a_onehot_seq[ix_seq,...]=encode_1hot_single_sequence(line.upper(),label_encoder,onehot_encoder)
        ix_seq += 1
    if ix_seq==BATCH_SIZE:
        print('check')
        try:
            sequences = handle_sequences(X=a_onehot_seq)
        except:
            print('an error')
        break
        
print(str(ix_seq))
write_pswm(sequences)
