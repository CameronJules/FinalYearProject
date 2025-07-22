# Serverless Audio Proecssing

## Overview
As part of my final year project I created a severless API to provide access to audio processing and machine learning functionalities.

The intention behind the project was to abstract the mathematical detail behind the functionality, reducing the overhead in creating web applications with audio functionalities.

The functions have been created using libraries and direct implementations, which have subsequently tested under different serverless configurations to understand cost and performance trade-offs.  

## How to
### Run functions
The functions are designed to run on AWS lambda. Howerver, for a given function the basic python code can be taken and run seperately from the lambda handler logic.

If using the code on lambda look for dockerfiles. If there is no docker file then the dependencies can be added to lambda via [zip files](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-dependencies) or [layers](https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html). Otherwise the the code and dependencies can be provided by [container images](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html).

<br>NOTE: when using the [essentia](https://essentia.upf.edu/index.html) library for container images you might need to build the latest version of essentia from source.

### View testing results
To see some of the results of testing check the analysis folder and view the notebook files which have some graphed versions of test data.
