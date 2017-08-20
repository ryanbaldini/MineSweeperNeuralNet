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
    gamesPerBatch = 100
    epochsPerBatch = 1
    try:
        opts, args = getopt.getopt(argv, "ho:m:b:g:e:", ["option=", "model=", "batches=", "gamesPerBatch=", "epochsPerBatch="])
    except getopt.GetoptError:
        print 'trainModelBackground.py -o <option> -m <model>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'trainModelBackground.py -o <option> -m <model>'
            sys.exit()
        elif opt in ("-o", "--option"):
            option = arg
        elif opt in ("-m", "--model"):
            modelChoice = arg
        elif opt in ("-b", "--batches"):
            nBatches = int(arg)
        elif opt in ("-g", "--gamesPerBatch"):
            gamesPerBatch = int(arg)
        elif opt in ("-e", "--epochsPerBatch"):
            epochsPerBatch = int(arg)

    if option == "trainNew":
        modelSource = imp.load_source("modelCode/" + modelChoice + ".py")
        model = modelSource.model
        dim = modelSource.dim
    elif option == "continueTraining":
        model = load_model("trainedModels/" + modelChoice + ".h5")
        dim = model.get_config()['layers'][0]['config']['batch_input_shape'][2]  # pulled from keras config

    learner = MineSweeperLearner(modelChoice, model, dim)
    learner.learnMineSweeper(gamesPerBatch, nBatches, epochsPerBatch, verbose=True)

    learner.model.save("trainedModels/" + modelChoice + ".h5")

if __name__ == "__main__":
   main(sys.argv[1:])
