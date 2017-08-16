import numpy as np
from MineSweeperLearner import MineSweeperLearner
import os
import imp
from keras.models import load_model

np.set_printoptions(linewidth = 500)

#Prompt user to specify the model they want to use
#get raw model code
models = os.listdir("modelCode")
models = [i.replace(".py","") for i in models if not ".pyc" in i and i[0] != '.']
#and pre-trained models
preTrainedModels = os.listdir("trainedModels")
preTrainedModels = [i.replace(".h5","") for i in preTrainedModels if i[0] != '.']
toDo = input("What do you want to do? \n1. Train a new model from scratch \n2. Keep training a pre-trained model\n")
if toDo == 1:
    prompt = "Choose which model to train (from 'modelCode' folder): \n"
    for i in range(len(models)):
        prompt += str(i+1) +  ". " + models[i] + '\n'
    modelChoice = input(prompt)
    modelChoice = models[modelChoice-1]
    modelSource = imp.load_source(modelChoice, "modelCode/" + modelChoice + ".py")
    model = modelSource.model
    dim = modelSource.dim
elif toDo == 2:
    prompt = "Choose which model to continue training (from 'trainedModels' folder): \n"
    for i in range(len(preTrainedModels)):
        prompt += str(i+1) +  ". " + preTrainedModels[i] + '\n'
    modelChoice = input(prompt)
    modelChoice = preTrainedModels[modelChoice-1]
    model = load_model("trainedModels/" + modelChoice + ".h5")
    dim = model.get_config()['layers'][0]['config']['batch_input_shape'][2] #pulled from keras config

#now train
learner = MineSweeperLearner(model, dim)
gamesPerBatch = input("How many games per batch? ")
nBatches = input("How many batches? ")
learner.learnMineSweeper(gamesPerBatch, nBatches, verbose=True)

#save model
learner.model.save("trainedModels/" + modelChoice + ".h5")
