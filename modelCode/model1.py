from keras.models import Model
from keras.layers import Input
from keras.layers.convolutional import Conv2D
from keras.layers.merge import Multiply

dim = 10
inputShape = (11,dim,dim)   #11 channels, each 10x10

in1 = Input(shape=inputShape)
in2 = Input(shape=(1,dim,dim))
conv = Conv2D(16, (5,5), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(in1)
conv = Conv2D(8, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(1, (1,1), padding='same', data_format = 'channels_first', activation = 'sigmoid', use_bias = True)(conv)
out = Multiply()([conv,in2])
model = Model(inputs=[in1,in2], outputs=out)
model.compile(loss='binary_crossentropy',optimizer='adadelta')
