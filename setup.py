from setuptools import setup

setup(name='carl',
      version='0.0.1',
      description='Car game for reinforcement learning',
      url='https://github.com/MatthiasSchinzel/CaRL',
      author='Matthias Schinzel',
      author_email='unused@unused.com',
      license='MIT',
      packages=['ca-rl'],
      install_requires=[
        'opencv-python>=4',
        'numpy>=1',
        'pygame>=1',
      ],
      package_data={
        'Tracks': ['*.png']
      },
      include_package_data=True,
      zip_safe=False)
