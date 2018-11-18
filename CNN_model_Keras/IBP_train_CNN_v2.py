'''
Created on 17 Nov 2018

@author: wimth
'''

import numpy as np
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder       
from keras.models import Sequential
from keras.layers import TimeDistributed,LSTM,Bidirectional
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv1D, MaxPooling1D
from keras.callbacks import ModelCheckpoint, EarlyStopping,TensorBoard
from keras.utils import plot_model
from sklearn.utils import class_weight
from sklearn.metrics import roc_curve,auc
from keras.models import load_model
import matplotlib.pyplot as plt
from itertools import cycle

WORK_DIR = r'E:\Downloads\IBP_project\Deep_learing_model'
FILE_INPUT_TRAIN = 'deep_learning_train_shuffled.fna'
NB_SEQUENCES_IN_TRAINFILE = round(sum(1 for line in open(os.path.join(WORK_DIR,FILE_INPUT_TRAIN)))/2)

FILE_INPUT_TEST = 'deep_learning_test.fna'
NB_SEQUENCES_IN_TESTFILE = round(sum(1 for line in open(os.path.join(WORK_DIR,FILE_INPUT_TEST)))/2)

LOAD_MODEL_FROM_DISK = True
FILE_NAME_MODEL_FROM_DISK = 'best_model.01-0.67.h5'
MODEL_TO_USE = '2'

BATCH_SIZE_TRAIN = 2000
BATCH_SIZE_TEST = 200
EPOCHS = 10
SEQ_LENGTH=815
ONEHOT_LABEL_P = np.asarray([1,0])
ONEHOT_LABEL_I = np.asarray([0,1])


def encode_1hot_single_label(input_string):
    if input_string[-1:]=='P':
        return ONEHOT_LABEL_P
    elif input_string[-1:]=='I':
        return ONEHOT_LABEL_I
    else:
        print('warning : no label found ! defaulting to label P')
        return ONEHOT_LABEL_P


def encode_1hot_single_sequence(input_string,label_encoder,onehot_encoder):
    integer_encoded = label_encoder.fit_transform(np.array(list(input_string))) #will give numeric values, alphabetically, so encoding will be similar for all sequences (A=0, C=1, G=2, T=3)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
    if onehot_encoded.shape[1]==5 and 'N' in input_string:  #some sequences contain 'N', this will be the fourth column(only 18 present in trainingset) => cut the 'N'-column, the 'N's will be encoded with all zeros
        onehot_encoded = np.delete(onehot_encoded,3,axis=1)
    return onehot_encoded


def generate_data_in_batch_size(TrainOrTest='train'):
        
    while 1:
        if TrainOrTest=='test':
            BATCH_SIZE = BATCH_SIZE_TEST
            f = open(os.path.join(WORK_DIR,FILE_INPUT_TEST))
        else:
            BATCH_SIZE=BATCH_SIZE_TRAIN
            f = open(os.path.join(WORK_DIR,FILE_INPUT_TRAIN))
            
        a_onehot_seq = np.zeros((BATCH_SIZE,SEQ_LENGTH,4))
        a_onehot_label = np.zeros((BATCH_SIZE,2))
        label_encoder = LabelEncoder()
        onehot_encoder = OneHotEncoder(sparse=False)
        ix_label = 0;ix_seq =0

        for line in f:
            line=line.rstrip()
            if line.startswith('>'):
                a_onehot_label[ix_label,...] = encode_1hot_single_label(line)
                ix_label +=1
            else:
                a_onehot_seq[ix_seq,...]=encode_1hot_single_sequence(line.upper(),label_encoder,onehot_encoder)
                ix_seq += 1

            if ix_seq==BATCH_SIZE:
                yield (a_onehot_seq, a_onehot_label)
                a_onehot_label = np.zeros((BATCH_SIZE,2))
                a_onehot_seq = np.zeros((BATCH_SIZE,SEQ_LENGTH,4))
                ix_label = 0;ix_seq =0
        f.close()

def get_onehot_labels(testOrTrain='test'):
    
    if testOrTrain=='test':
        nb_sequences = NB_SEQUENCES_IN_TESTFILE
        file = FILE_INPUT_TEST
    elif testOrTrain=='train':
        nb_sequences = NB_SEQUENCES_IN_TRAINFILE
        file = FILE_INPUT_TRAIN
        
    a_onehot_label = np.zeros((nb_sequences,2))
    ix_label=0
    for line in open(os.path.join(WORK_DIR,file)):
        line=line.rstrip()
        if line.startswith('>'):
            a_onehot_label[ix_label,...] = encode_1hot_single_label(line)
            ix_label +=1
            
    return a_onehot_label
    
    
    
def get_weights_labels(testOrTrain='train'):
    
    if testOrTrain=='train':
        file = FILE_INPUT_TRAIN
    elif testOrTrain=='test':
        file = FILE_INPUT_TEST
    
    l_labels= []
    with open(os.path.join(WORK_DIR,file)) as f: 
        for line in f: 
            line=line.rstrip()
            if line.startswith('>'):
                l_labels.append(line[-1:])

    return class_weight.compute_class_weight('balanced', np.unique(l_labels), l_labels)

def build_model_1():
    model = Sequential()
    model.add(Conv1D(activation="relu",    #the output shape of this will be (815-(26-1),320)
                 input_shape=(SEQ_LENGTH, 4), 
                 filters=320, 
                 kernel_size=26, 
                 strides=1, 
                 padding="valid"))

    model.add(MaxPooling1D(pool_size=13, strides=13)) #the output shape of this will be ((815-(26-1))/13,320)
    model.add(Dropout(0.3))
    
    model.add(Flatten())
    model.add(Dense(500,activation='relu'))
    
    model.add(Dense(2,activation='softmax'))
    
    print ('compiling model')
    model.compile(loss='binary_crossentropy', 
                  optimizer='adam',
                  metrics=['accuracy'])
    #plotting model
    plot_model(model, to_file=os.path.join(WORK_DIR,'IBP_model.png'))
    print(model.summary())
    
    return model

def build_model_2():
    model = Sequential()
    model.add(Conv1D(300, kernel_size=19, padding="valid", activation='relu', input_shape=(SEQ_LENGTH, 4)))
    model.add(MaxPooling1D(pool_size=4, strides=4, padding='valid'))
    model.add(Dropout(0.20))
    model.add(Conv1D(200, kernel_size=11, padding="valid", activation='relu'))
    model.add(MaxPooling1D(pool_size=4, strides=4, padding='valid'))
    model.add(Dropout(0.20))
    model.add(Conv1D(200, kernel_size=7, padding="valid", activation='relu'))
    model.add(MaxPooling1D(pool_size=4, strides=4, padding='valid'))
    model.add(Dropout(0.20))
    model.add(Flatten())
    model.add(Dense(925))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(2, activation='softmax'))
    model.summary()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def build_model_3():
    model = Sequential()
    model.add(Conv1D(32, kernel_size=26, padding="valid", activation='relu', kernel_initializer='random_uniform',  input_shape=(SEQ_LENGTH, 4)))
    model.add(Dropout(0.2))
    model.add(TimeDistributed(Dense(32, activation='relu')))
    model.add(MaxPooling1D(pool_size=13, strides=13, padding='valid'))
    model.add(Bidirectional(LSTM(32, dropout=0.1, recurrent_dropout=0.1, return_sequences=True)))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.4))
    model.add(Dense(2, activation='softmax'))
    model.summary()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def do_ROC_evaluation(y_pred_keras,y_test,show_plot,save_plot):
    # Compute ROC curve and ROC area for each class
    print('starting ROC evaluation')
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    
    for i in range(2):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_pred_keras[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Compute micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_pred_keras.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    plot_ROC_curve(fpr,tpr,roc_auc,show_plot,save_plot)
    
    return [fpr,tpr,roc_auc]


def plot_ROC_curve(fpr,tpr,roc_auc,show_plot=False,save_plot=True):
    lw = 2
    plt.figure(1)
    plt.plot(fpr["micro"], tpr["micro"],
         label='micro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["micro"]),
         color='deeppink', linestyle=':', linewidth=4)

    
    colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
    for i, color in zip(range(2), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                 label='ROC curve of class {0} (area = {1:0.2f})'
                 ''.format(i, roc_auc[i]))
        
    plt.plot([0, 1], [0, 1], 'k--')
    #plt.plot(fpr_keras, tpr_keras, label='Keras (area = {:.3f})'.format(auc_keras))
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC curve')
    plt.legend(loc='best')
    
    if save_plot:plt.savefig(os.path.join(WORK_DIR,'ROC_curve_model{0}.png'.format(MODEL_TO_USE)))
    if show_plot:plt.show()
  
#MAIN---------------------------------------------------------------

if LOAD_MODEL_FROM_DISK:
    print('#loading the model')
    model = load_model(os.path.join(WORK_DIR,FILE_NAME_MODEL_FROM_DISK))
    print('model {0} is loaded'.format(FILE_NAME_MODEL_FROM_DISK))
else:
    print('#building the model')
    if MODEL_TO_USE=='2':
        model = build_model_2()
    elif MODEL_TO_USE=='1':
        model = build_model_1()
    elif MODEL_TO_USE=='3':
        model = build_model_3()
    
    #training the model
    print('training the model')
    label_weights = get_weights_labels('train')
    
    callbacks_list = [
        ModelCheckpoint(filepath=os.path.join(WORK_DIR,'best_model{MODEL_TO_USE}.{epoch:02d}-{acc:.2f}.h5'),
                                        monitor='loss',
                                        mode='min', 
                                        save_best_only=True),
        EarlyStopping(monitor='acc', patience=3,verbose=1),
        TensorBoard(log_dir=os.path.join(WORK_DIR,'./logs'))
    ]
    
    model.fit_generator(generate_data_in_batch_size('train'),
                        shuffle=True,
                        class_weight=label_weights,
                        callbacks=callbacks_list,
                        steps_per_epoch=round(NB_SEQUENCES_IN_TRAINFILE/BATCH_SIZE_TRAIN), 
                        epochs=EPOCHS)


print('predicting with the test data')
nb_steps = round (NB_SEQUENCES_IN_TESTFILE/BATCH_SIZE_TEST)
nb_test_cases = nb_steps * BATCH_SIZE_TEST
y_pred_keras = model.predict_generator(generate_data_in_batch_size('test'),
                                       steps=nb_steps,
                                       verbose=1
                                       )

y_test = get_onehot_labels('test')[0:nb_test_cases,:]
print('->label distribution of test set = {0}, corresponding to weights {1}'.format(np.sum(y_test,axis=0),get_weights_labels('test')))
print('->label distribution of predicted set = {0}'.format(np.sum(y_pred_keras,axis=0)))

do_ROC_evaluation(y_pred_keras,y_test,show_plot=False,save_plot=True)
test_loss = model.evaluate_generator(generate_data_in_batch_size('test'), steps=nb_steps)
print('test set evaluation metrics =>  {2} = {0} ; {3} = {1}'.format(test_loss[0],test_loss[1],model.metrics_names[0],model.metrics_names[1]))


print('end')
