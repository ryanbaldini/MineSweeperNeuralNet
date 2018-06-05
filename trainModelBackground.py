from MineSweeperLearner import MineSweeperLearner
import imp
import sys, getopt
from keras.models import load_model

#called like this:
#python trainModelBackground.py -o [option] -m [model] -b [batches] -g [gamesPerBatch]

def main(argv):
    option = ''
    modelChoice = ''
    nBatches = 1000
    nSamples = 1000
    epochsPerBatch = 1
    try:
        opts, args = getopt.getopt(argv, "ho:m:b:s:e:", ["option=", "model=", "batches=", "nSamples=", "epochsPerBatch="])
    except getopt.GetoptError:
        print('trainModelBackground.py -o <option> -m <model>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('trainModelBackground.py -o <option> -m <model>')
            sys.exit()
        elif opt in ("-o", "--option"):
            option = arg
        elif opt in ("-m", "--model"):
            modelChoice = arg
        elif opt in ("-b", "--batches"):
            nBatches = int(arg)
        elif opt in ("-s", "--nSamples"):
            nSamples = int(arg)
        elif opt in ("-e", "--epochsPerBatch"):
            epochsPerBatch = int(arg)

    if option == "trainNew":
        modelSource = imp.load_source(modelChoice, "modelCode/" + modelChoice + ".py")
        model = modelSource.model
    elif option == "continueTraining":
        model = load_model("trainedModels/" + modelChoice + ".h5")

    learner = MineSweeperLearner(modelChoice, model)
    learner.learnMineSweeper(nSamples, nBatches, epochsPerBatch, verbose=True)

    learner.model.save("trainedModels/" + modelChoice + ".h5")

if __name__ == "__main__":
   main(sys.argv[1:])
