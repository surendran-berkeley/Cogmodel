from keras.layers import Input, Dense, Embedding, LSTM, merge, TimeDistributed
from keras.models import Model
from keras.optimizers import Adagrad, RMSprop, Adagrad, Adam, Adamax, Optimizer
import numpy as np
from keras.callbacks import History




def slice_function(input_file):
    a= input_file
    eid= input_file[:,: ,0]
    return eid

test_size=1000
epoch=4
#optimizers=["Adagrad(clipnorm=0.1   )", "RMSprop(clipnorm=0.1)", "Adadelta(clipnorm=0.1)", "Adam(clipnorm=0.1)", "Adamax(clipnorm=0.1)", "Nadam(clipnorm=0.1)"]
random_rows= np.random.randint(12300, size= test_size ) #creating a matrix for test data




input_matrix=np.load("input_tensor.npy")
output_all=np.load("output_tensor.npy")[:,:,:]
weight=np.load("output_mask.npy")[:,:,:]


prediction_list=[]
dict_weight_mode={}
dict_sample_weight={}
dict_loss={}
dict_metric={}
y_labels_list=[]

event_in_slice=slice_function(input_matrix)


#delete multiple rows from the main matrix to remove the test set and create a training set
event_input=np.delete(event_in_slice, random_rows, 0 )[:120]
output= np.delete(output_all, random_rows, 0 )[:120]
weight_mask=np.delete(weight, random_rows, 0 )[:120]

#extract multiple elements from the main matrix to generate a test set
x_test=event_in_slice[np.array(random_rows)]
y_test=output_all[np.array(random_rows)]
y_mask=weight[np.array(random_rows)]

print (event_input.shape)
print (output.shape)
print (weight_mask.shape)
input_dim_length=len(event_input[0])




def model (optimizer_type, event_input, output, weight_mask, x_test, epoch):
    optimizer_type= Adagrad()
    print(optimizer_type)
    print (event_input.shape)
    print (output.shape)
    print (weight_mask.shape)
    inputs_eid = Input(shape=(1209, ), dtype="int16")#should I provide the z axis  dimension too?

    embedding_layer=Embedding(input_dim=4347, output_dim=64, input_length=1209, mask_zero=True)(inputs_eid) #4347 because we need the voabl lenght plus 1
    print (embedding_layer)
    one_lstm=LSTM(32, return_sequences= True)(embedding_layer)
    for i in range(len(output[0,0,:])):
        name="prediction_"+ str(i)
        prediction=TimeDistributed(Dense(1, activation="sigmoid" ),name =name)(one_lstm)
        prediction_list.append(prediction)
        dict_weight_mode[name]="temporal"
        dict_sample_weight[name]=weight_mask[:,:,i]
        dict_loss[name]="binary_crossentropy"
        dict_metric[name]="accuracy"
        y_labels_list.append(output[:,:,i:(i+1)])

    print (y_labels_list[0].shape) #check the shape of output
    print (dict_sample_weight["prediction_0"].shape) #check the shape of the mask

    model=Model(input=inputs_eid, output=prediction_list)

    model.compile(optimizer=optimizer_type,loss=dict_loss, sample_weight_mode=dict_weight_mode) # Originally used 'rmsprop' for optimiser .... / metrics=dict_metric ////Is temporal the right thing?

    #history=model.train_on_batch(event_input, y_labels_list, sample_weight=dict_sample_weight) # The documentation at Keras says that in the 'case of temporal data you can pass a 2d array with shape (sample, sequence_lenght ) to apply to different weights. If so how de we apply a 3d tensor as a sample weight matrix'
    history=model.fit(event_input, y_labels_list, sample_weight=dict_sample_weight, nb_epoch=epoch, batch_size=128) # The documentation at Keras says that in the 'case of temporal data you can pass a 2d array with shape (sample, sequence_lenght ) to apply to different weights. If so how de we apply a 3d tensor as a sample weight matrix'

    model_loss=history.history
    model_value=model.get_value()
    print(model_value)
    """model_gradient=optimizer_type.get_gradients(loss=model_loss)

    print("The models gradient history is")
    print (model_gradient)
"""

a=model("Adagrad", event_input, output, weight_mask, x_test, epoch)
np.save("model_check", a)
#adam, rmsprop, Adagrad, Adamax
