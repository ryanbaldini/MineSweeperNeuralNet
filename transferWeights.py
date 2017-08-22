from keras.models import load_model

oldModel = load_model("oldModels/model6.h5")
newModel = load_model("trainedModels/model6.h5")

#The following code is specific to model6's architecture. It doesn't apply in general.

for i in range(1,6):
    newModel.layers[i].set_weights(oldModel.layers[i].get_weights())

newModel.save("trainedModels/model6Transferred.h5")
