from setuptools import setup

setup(name='car-rl',
      version='0.0.1',
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
      zip_safe=False)
