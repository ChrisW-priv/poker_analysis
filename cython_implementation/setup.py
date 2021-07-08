from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("poker_analysis.pyx")
)

# $ python setup.py build_ext --inplace
