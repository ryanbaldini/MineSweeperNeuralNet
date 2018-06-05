import os
from MineSweeperLearner import MineSweeperLearner
from keras.models import load_model
import numpy as np

np.set_printoptions(linewidth = 1000, precision=3, suppress=True)

#Prompt user to specify the model they want to watch play
preTrainedModels = os.listdir("trainedModels")
preTrainedModels = [i.replace(".h5","") for i in preTrainedModels if i[0] != '.']
preTrainedModels = np.sort(preTrainedModels)
prompt = "Which model do you want to watch play? \n"
for i in range(len(preTrainedModels)):
    prompt += str(i + 1) + ". " + preTrainedModels[i] + '\n'
modelChoice = int(input(prompt))
modelChoice = preTrainedModels[modelChoice - 1]

model = load_model("trainedModels/" + modelChoice + ".h5")

learner = MineSweeperLearner(modelChoice, model)
learner.watchMePlay()