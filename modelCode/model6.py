from keras.models import Model
from keras.layers import Input
from keras.layers.convolutional import Conv2D
from keras.layers.merge import Multiply

dim1 = 16
dim2 = 30
inputShape = (11,dim1,dim2)   #11 channels

in1 = Input(shape=inputShape)
in2 = Input(shape=(1,dim1,dim2))
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(in1)
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(64, (3,3), padding='same', data_format = 'channels_first', activation = 'relu', use_bias = True)(conv)
conv = Conv2D(1, (1,1), padding='same', data_format = 'channels_first', activation = 'sigmoid', use_bias = True)(conv)
out = Multiply()([conv,in2])
model = Model(inputs=[in1,in2], outputs=out)
model.compile(loss='binary_crossentropy',optimizer='adadelta')

