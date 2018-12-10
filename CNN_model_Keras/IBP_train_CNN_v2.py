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
from sklearn.metrics import average_precision_score,precision_recall_curve
from sklearn.utils.fixes import signature
from keras.models import load_model
import matplotlib.pyplot as plt
import random   
from viz_sequence import plot_weights


STRIDE = 20
WORK_DIR = ''
FILE_INPUT = 'deep_learning' + '_stride' + str(STRIDE)

LOAD_MODEL_FROM_DISK = True

if not LOAD_MODEL_FROM_DISK:
    FILE_INPUT_TRAIN = FILE_INPUT + '_train_shuffled.fna'
    NB_SEQUENCES_IN_TRAINFILE = round(sum(1 for line in open(os.path.join(WORK_DIR,FILE_INPUT_TRAIN)))/2)
    RANDOM_PERC_TRAIN_DATA = '' #if '' then train on full train set
    
    FILE_INPUT_VALIDATION = FILE_INPUT + '_val_shuffled.fna'
    NB_SEQUENCES_IN_VALIDATIONFILE = round(sum(1 for line in open(os.path.join(WORK_DIR,FILE_INPUT_VALIDATION)))/2)

FILE_INPUT_TEST = FILE_INPUT + '_test_shuffled.fna'
NB_SEQUENCES_IN_TESTFILE = round(sum(1 for line in open(os.path.join(WORK_DIR,FILE_INPUT_TEST)))/2)

if not LOAD_MODEL_FROM_DISK:
    print('NB TRAIN RECORDS = {0}, NB VALIDATION RECORDS = {1}, NB_TEST_RECORDS = {2}'.format(NB_SEQUENCES_IN_TRAINFILE,NB_SEQUENCES_IN_VALIDATIONFILE,NB_SEQUENCES_IN_TESTFILE))
else:
    print('NB_TEST_RECORDS = {0}'.format(NB_SEQUENCES_IN_TESTFILE))
    
FILE_OUTPUT_MOTIFS = 'predicted_motifs'


PLOT_MOTIFS = False

#FILE_NAME_MODEL_FROM_DISK = 'best_model.09-0.79_MODEL3.h5'
FILE_NAME_MODEL_FROM_DISK = 'best_model.02-0.61_MODEL2.h5'
#FILE_NAME_MODEL_FROM_DISK = 'best_model.08-0.79_MODEL3.h5'
MODEL_TO_USE = '2'
MODEL2_COMPARE_PERFORMANCE = 'best_model.08-0.79_MODEL3.h5'
#MODEL2_COMPARE_PERFORMANCE = ''

BATCH_SIZE_TRAIN = 200
BATCH_SIZE_TEST = 73
BATCH_SIZE_VALIDATION = int((BATCH_SIZE_TRAIN/8))

EPOCHS = 20
SEQ_LENGTH=815
ONEHOT_LABEL_P = np.asarray([0,1])
ONEHOT_LABEL_I = np.asarray([1,0])

L_NUCLEOTIDES = ['A','C','G','T']


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


def create_random_subset_train_data():
    
    global FILE_INPUT_TRAIN, NB_SEQUENCES_IN_TRAINFILE 
    f_in = open(os.path.join(WORK_DIR,FILE_INPUT_TRAIN))
    
    f_out_name = FILE_INPUT_TRAIN[:-4]+ '_' + str(RANDOM_PERC_TRAIN_DATA) + 'PERC.fna'
    f_out_nb_rec = round(NB_SEQUENCES_IN_TRAINFILE*(RANDOM_PERC_TRAIN_DATA/100))
    f_out = open(os.path.join(WORK_DIR,f_out_name),'w')
    print('making a subset selection of the training data {0}'.format(f_out_name))
    
    l_ix_rand = random.sample(range(NB_SEQUENCES_IN_TRAINFILE), f_out_nb_rec)
    ix_fasta =0
    for line in f_in:
        if ix_fasta in l_ix_rand:
            f_out.write(line)
            
        if not line.startswith('>'):
            ix_fasta +=1
    
    f_in.close()
    f_out.close()
    
    FILE_INPUT_TRAIN = f_out_name
    NB_SEQUENCES_IN_TRAINFILE = f_out_nb_rec

    return

def generate_validation_data_in_batch_size():
        
    while 1:

        BATCH_SIZE = BATCH_SIZE_VALIDATION
        f = open(os.path.join(WORK_DIR,FILE_INPUT_VALIDATION))
        
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
    
    l_weights = class_weight.compute_class_weight('balanced', np.unique(l_labels), l_labels)
    
    print('l_weights from sklearn module=',l_weights,' with unique labels=',np.unique(l_labels))

    d_keras_weights = {ix:weight for ix,weight in enumerate(l_weights)}

    return [l_weights,d_keras_weights]

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
    model.add(Conv1D(30, kernel_size=19, padding="valid", activation='relu', input_shape=(SEQ_LENGTH, 4)))
    model.add(MaxPooling1D(pool_size=4, strides=4, padding='valid'))
    model.add(Dropout(0.20))
    model.add(Conv1D(20, kernel_size=11, padding="valid", activation='relu'))
    model.add(MaxPooling1D(pool_size=4, strides=4, padding='valid'))
    model.add(Dropout(0.20))
    model.add(Conv1D(20, kernel_size=7, padding="valid", activation='relu'))
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

def do_ROC_evaluation(y_pred_keras,y_test,show_plot=False,save_plot=True,model2=True):

    print('starting ROC evaluation')
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    # Compute ROC curve and ROC area (=average
    fpr["model1"], tpr["model1"], _ = roc_curve(y_test.ravel(), y_pred_keras.ravel())
    roc_auc["model1"] = auc(fpr["model1"], tpr["model1"])
    
    if MODEL2_COMPARE_PERFORMANCE:
        fpr["model2"], tpr["model2"], _ = roc_curve(y_test.ravel(), y_pred2_keras.ravel())
        roc_auc["model2"] = auc(fpr["model2"], tpr["model2"])
        
    # plot the curve
    plot_ROC_curve(fpr,tpr,roc_auc,show_plot,save_plot)
    
    return [fpr,tpr,roc_auc]


def plot_ROC_curve(fpr,tpr,roc_auc,show_plot=False,save_plot=True,model2=True):

    plt.figure(1)
    plt.plot(fpr["model1"], tpr["model1"],
             label='Model 1(area = {0:0.2f})'.format(roc_auc["model1"]),
             color='deeppink', linestyle=':', linewidth=4)
    
    if MODEL2_COMPARE_PERFORMANCE:
        plt.plot(fpr["model2"], tpr["model2"],
                 label='Model 2(area = {0:0.2f})'.format(roc_auc["model2"]),
                 color='green', linestyle=':', linewidth=4)

    plt.plot([0, 1], [0, 1], 'k--')
    #plt.plot(fpr_keras, tpr_keras, label='Keras (area = {:.3f})'.format(auc_keras))
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC curve')
    plt.legend(loc='best')
    
    if save_plot:plt.savefig(os.path.join(WORK_DIR,'ROC_curve_compare_models_{0}.png'.format(FILE_NAME_MODEL_FROM_DISK)))
    if show_plot:plt.show()


def write_motifs():
    a_motif_weights = model.layers[0].get_weights()[0] 
    nb_motifs = a_motif_weights.shape[2]
    motif_length = a_motif_weights.shape[0]
    
    full_path = os.path.join(WORK_DIR,FILE_OUTPUT_MOTIFS + '_model' + str(MODEL_TO_USE) + '.txt')
    with open(full_path, 'w') as f:
        for ix_motif in range(0,nb_motifs):
            s_motif = ''
            for ix_nt in range(0,motif_length):
                s_motif += L_NUCLEOTIDES[np.argmax(a_motif_weights[ix_nt,:,ix_motif])]
            f.write(s_motif + "\n")
            
    return

def plot_motifs_from_weights(show=False):
    motif_raw_weights = model.layers[0].get_weights()[0]
    nb_motifs = motif_raw_weights.shape[2]
    motif_length = motif_raw_weights.shape[0]
    with open(os.path.join(WORK_DIR,'motifPSWM_' + FILE_NAME_MODEL_FROM_DISK[0:-3] + '.motif'),'w',newline='') as f_motif:
        for ix_motif in range(0,nb_motifs):
            motif_raw = motif_raw_weights[...,ix_motif]
            motif_clipped = motif_raw.clip(min=0)
            motif_scaled = motif_clipped/np.max(motif_clipped)
            
            f_motif.write('>motif{0}{1}'.format(ix_motif,"\n"))
            for ix_pos in range(motif_length):
                for ix_nucleotide in range(0,4):
                    f_motif.write(str(motif_scaled[ix_pos,ix_nucleotide]))
                    if ix_nucleotide==3:
                        f_motif.write('\n') 
                    else:
                        f_motif.write('\t') 
                   
            if show:plot_weights(motif_scaled)
    
    return


def plot_PR_curve(y_pred_keras,y_test,show_plot=False,save_plot=True,model2=True,use_I_as_pos=False):
    
    if use_I_as_pos:ix_col=0
    else:ix_col=1
    
    plt.figure(2)
    a_y_test = np.asarray(y_test)#[:,ix_col]
    
    step_kwargs = ({'step': 'post'} if 'step' in signature(plt.fill_between).parameters else {}) # In matplotlib < 1.5, plt.fill_between does not have a 'step' argument
        
    a_y_pred_keras = np.asarray(y_pred_keras)#[:,ix_col]
    precision, recall, _ = precision_recall_curve(a_y_test.ravel(), a_y_pred_keras.ravel())
    plt.step(recall, precision, color='deeppink', alpha=0.2,where='post')
    plt.fill_between(recall, precision, alpha=0.2, color='deeppink', label ='Model 1 (AP={0:0.2f})'.format(average_precision), **step_kwargs)
    
    if MODEL2_COMPARE_PERFORMANCE:
        a_y_pred2_keras = np.asarray(y_pred2_keras)#[:,ix_col]
        precision, recall, _ = precision_recall_curve(a_y_test.ravel(), a_y_pred2_keras.ravel())
        plt.step(recall, precision, color='green', alpha=1, where='post')
        plt.fill_between(recall, precision, alpha=1, color='green', label ='Model 2 (AP={0:0.2f})'.format(average_precision_2), **step_kwargs)
        
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    if use_I_as_pos:plt.title('Precision-Recall curve (I-label = positive)')
    else:plt.title('Precision-Recall curve (P-label = positive)')
    plt.title('Precision-Recall curve')
    plt.legend(loc='best')
    
    if use_I_as_pos:plot_suffix= 'Ipos'
    else:plot_suffix= 'Ppos'
    plot_suffix= ''
    if save_plot:plt.savefig(os.path.join(WORK_DIR,'PR_curve_compare_models_{1}_{0}.png'.format(FILE_NAME_MODEL_FROM_DISK,plot_suffix)))
    if show_plot:plt.show()

    return

def load_model_from_disk(file_name_model):
    
    print('#loading the model')
    model = load_model(os.path.join(WORK_DIR,file_name_model))
    print('model {0} is loaded'.format(file_name_model))
    
    return model


    

#MAIN---------------------------------------------------------------

if LOAD_MODEL_FROM_DISK:
    model = load_model_from_disk(FILE_NAME_MODEL_FROM_DISK)
else:
    print('#building the model')
    if RANDOM_PERC_TRAIN_DATA:create_random_subset_train_data()
    
    if MODEL_TO_USE=='2': model = build_model_2()
    elif MODEL_TO_USE=='1':model = build_model_1()
    elif MODEL_TO_USE=='3':model = build_model_3()
    
    #training the model
    print('training the model')
    callbacks_list = [
        ModelCheckpoint(filepath=os.path.join(WORK_DIR,'best_model.{epoch:02d}-{acc:.2f}_MODEL' + MODEL_TO_USE + '.h5'),
                                        monitor='val_acc',
                                        mode='max', 
                                        save_best_only=False),
        EarlyStopping(monitor='val_acc', patience=10
                      ,verbose=1),
  
        TensorBoard(log_dir=os.path.join(WORK_DIR,'./logs'))
    ]
    
    model.fit_generator(generate_data_in_batch_size('train'),
                        shuffle=True,
                        class_weight=get_weights_labels('train')[1],
                        callbacks=callbacks_list,
                        steps_per_epoch=round(NB_SEQUENCES_IN_TRAINFILE/BATCH_SIZE_TRAIN), 
                        validation_data=generate_validation_data_in_batch_size(),
                        validation_steps=round(NB_SEQUENCES_IN_VALIDATIONFILE/BATCH_SIZE_VALIDATION),
                        epochs=EPOCHS)

print('writing motifs')
write_motifs()
if PLOT_MOTIFS:plot_motifs_from_weights(show=True)

print('predicting with the test data')
nb_steps = round (NB_SEQUENCES_IN_TESTFILE/BATCH_SIZE_TEST)
nb_test_cases = nb_steps * BATCH_SIZE_TEST
y_pred_keras = model.predict_generator(generate_data_in_batch_size('test'),
                                       steps=nb_steps,
                                       verbose=1
                                       )

y_test = get_onehot_labels('test')[0:nb_test_cases,:]
print('->label distribution of test set = {0}, corresponding to weights {1}'.format(np.sum(y_test,axis=0),get_weights_labels('test')[0]))
print('->label distribution of predicted set = {0}'.format(np.sum(y_pred_keras,axis=0)))
# print('correct P = {0}'.format(sum(y_pred_keras[0:22805,1] >0.5)))
# print('wrong P   = {0}'.format(sum(y_pred_keras[0:22805,1] <0.5)))
# print('correct I   = {0}'.format(sum(y_pred_keras[22805:,0] >0.5)))
# print('wrong I   = {0}'.format(sum(y_pred_keras[22805:,0] <0.5)))




if MODEL2_COMPARE_PERFORMANCE:
    model2 = load_model_from_disk(MODEL2_COMPARE_PERFORMANCE)
    y_pred2_keras = model2.predict_generator(generate_data_in_batch_size('test'),
                                       steps=nb_steps,
                                       verbose=1
                                    )

    
do_ROC_evaluation(y_pred_keras,y_test)
test_loss = model.evaluate_generator(generate_data_in_batch_size('test'), steps=nb_steps)
print('test set evaluation metrics model 1 ({4}) =>  {2} = {0} ; {3} = {1}'.format(test_loss[0],test_loss[1],model.metrics_names[0],model.metrics_names[1],FILE_NAME_MODEL_FROM_DISK))
if MODEL2_COMPARE_PERFORMANCE:
    test_loss = model2.evaluate_generator(generate_data_in_batch_size('test'), steps=nb_steps)
    print('test set evaluation metrics model 2 ({4})=>  {2} = {0} ; {3} = {1}'.format(test_loss[0],test_loss[1],model.metrics_names[0],model.metrics_names[1],MODEL2_COMPARE_PERFORMANCE))

average_precision = average_precision_score(y_test, y_pred_keras)
print('Average precision-recall score model 1 ({1}): {0:0.2f}'.format(average_precision,FILE_NAME_MODEL_FROM_DISK))
if MODEL2_COMPARE_PERFORMANCE:
    average_precision_2 = average_precision_score(y_test, y_pred2_keras)
    print('Average precision-recall score model 2 ({1}): {0:0.2f}'.format(average_precision_2,MODEL2_COMPARE_PERFORMANCE))
    
plot_PR_curve(y_pred_keras,y_test)


