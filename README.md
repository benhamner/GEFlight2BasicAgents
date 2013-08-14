GE Flight Quest 2 - Flight Optimization
=======================================

This repo contains code to create a basic sample submission for the [GE Flight Quest 2: Flight Optimization competition](https://www.gequest.com/c/flight2/), hosted by [Kaggle](http://www.kaggle.com) with [General Electric](http://www.ge.com/).

Executing this benchmark requires Python >=2.7 along with the following packages:

 - pandas (version >=10.1)
 - geopy (version >= 0.94.2)

To run the sample code,

1. [Download testFlights.csv and airports.csv](https://www.gequest.com/c/flight2/data)
2. Copy the files to the src/ directory (or update src/utilities.py to point to these files)
3. Create sampleSubmission.csv running `python basicAgent.py`
4. [Make a submission](https://www.gequest.com/c/flight2/team/select) with the output file
