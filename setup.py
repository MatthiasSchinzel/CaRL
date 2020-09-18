from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='car-rl',
      version='0.7',
      description='Car game for reinforcement learning',
      url='https://github.com/MatthiasSchinzel/CaRL',
      author='Matthias Schinzel',
      author_email='unused@unused.com',
      license='MIT',
      packages=['carl'],
      install_requires=[
        'opencv-python>=4',
        'numpy>=1',
        'pygame>=1',
      ],
      package_data={
        'Tracks': ['*.png']
      },
      include_package_data=True,
      long_description=long_description,
      long_description_content_type='text/markdown',
      zip_safe=False)
