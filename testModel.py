import os
import numpy as np
from keras.models import load_model
from MineSweeperLearner import MineSweeperLearner

#Prompt user to specify the model they want to use
preTrainedModels = os.listdir("trainedModels")
preTrainedModels = [i.replace(".h5","") for i in preTrainedModels if i[0] != '.']
preTrainedModels = np.sort(preTrainedModels)
prompt = "Choose which model to continue training (from 'trainedModels' folder): \n"
for i in range(len(preTrainedModels)):
    prompt += str(i+1) +  ". " + preTrainedModels[i] + '\n'
modelChoice = int(input(prompt))
modelChoice = preTrainedModels[modelChoice-1]

print("Loading model...")
model = load_model("trainedModels/" + modelChoice + ".h5")
learner = MineSweeperLearner(modelChoice, model)

#get batch info
nGames = int(input("How many games to test on? "))

#go
learner.testMe(nGames)