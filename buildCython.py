from distutils.core import setup
from Cython.Build import cythonize
import numpy as np

setup(
  name = 'MineSweeper',
  ext_modules = cythonize("MineSweeper.pyx"), 
  include_dirs = [np.get_include()]
)

setup(
  name = 'MineSweeperLearner',
  ext_modules = cythonize("MineSweeperLearner.pyx"), 
  include_dirs = [np.get_include()]
)
