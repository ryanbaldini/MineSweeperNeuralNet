from keras.models import load_model
from keras.models import Model
from keras.layers import Input
from keras.layers.convolutional import Conv2D
from keras.layers.merge import Multiply
from numpy.random import normal

dim1 = 16
dim2 = 30
inputShape = (11,dim1,dim2)   #11 channels

in1 = Input(shape=inputShape)
in2 = Input(shape=(1,dim1,dim2))
conv = Conv2D(80, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(in1)
conv = Conv2D(80, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(80, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(80, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(1, (1,1), padding='same', data_format = 'channels_first', activation = 'sigmoid', use_bias = True)(conv)
out = Multiply()([conv,in2])
model = Model(inputs=[in1,in2], outputs=out)
model.compile(loss='binary_crossentropy',optimizer='adadelta')


#The following code is specific to model6's architecture. It doesn't apply in general.

oldModel = load_model("oldModels/model6.h5")

#copy first layer
weights = model.layers[1].get_weights()
oldWeights = oldModel.layers[1].get_weights()
weights[0] = normal(0, 0.01, weights[0].shape)
weights[0][:, :, :, 0:64] = oldWeights[0]  # copy over the first 64
weights[1] = normal(0, 0.01, weights[1].shape)
weights[1][0:64] = oldWeights[1]
model.layers[1].set_weights(weights)
#full conv layers
for i in range(2,5):
    weights = model.layers[i].get_weights()
    oldWeights = oldModel.layers[i].get_weights()
    weights[0] = normal(0, 0.01, weights[0].shape)
    weights[0][:, :, 0:64, 0:64] = oldWeights[0]  #copy over the first 64
    weights[1] = normal(0, 0.01, weights[1].shape)
    weights[1][0:64] = oldWeights[1]
    model.layers[i].set_weights(weights)
#final conv layers
weights = model.layers[5].get_weights()
oldWeights = oldModel.layers[5].get_weights()
weights[0] = normal(0, 0.01, weights[0].shape)
weights[0][:, :, 0:64, :] = oldWeights[0]  #copy over the first 64
weights[1] = normal(0, 0.01, weights[1].shape)
weights[1] = oldWeights[1]
model.layers[5].set_weights(weights)

model.save("trainedModels/model7Transferred.h5")
