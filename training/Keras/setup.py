'''Cloud ML Engine package configuration.'''
from setuptools import setup, find_packages

setup(name='DeepMeerkat',
      version='0.0.1',
      packages=find_packages(),
      include_package_data=True,
      description='DeepMeerkat Keras model on Cloud ML Engine',
      author='Ben Weinstein',
      author_email='benweinstein2010@gmail.com',
      license='Unlicense',
      install_requires=[
          'keras',
          'h5py'],
      zip_safe=False)