![.](https://github.com/vin-nag/GANs-n-reels/blob/master/Site/images/title.png "Logo")

*Creating Music Using a Generative Adversarial Network*

By Billard, Mitchell; Bishop, Robert; Elsisy, Moustafa; Graves, Caleb; Dr. Kolokolova, Antonina; Nagisetty, Vineel; and Northcott, Zachary: all affiliated with Memorial University of Newfoundland

## Table of Contents
* Introduction
* Usage
* More Info

## Introduction:
Our research aims to discover if successful AI image generative models can also be used to generate music.  We plan to use a Deconvolutional Generative Adversarial Network, a particular type of Artificial Neural Network, in an attempt to generate Irish music.

We hope to use the distinctive structure of Irish tunes to make them suitable for GAN-based music generation. Our main idea is to regard an Irish melody as a fixed-size object with cross-references among its parts:  “music as a picture” view.  The two key components of this project are:

* Preprocessing: 
  * Creating a well-defined format for music encoding suitable for GANs
  * Representing “vertical” dependencies in the tunes through a music as a picture view
* Modifying GANs via:
  * Structuring strides and kernel size to take advantage of observed features in image forms
  * Modifying training rate to avoid “Mode Collapse”	
 
 ## Usage:
 ### Source Code:
 * The Preprocessing code is found in the `src/Generation/` directory
 * The Neural Network training code is found in the `src/Model/` directory
 * The Data used for preprocessing and training is found in the `Data/` directory
 * The code for our website is found in the `Site/` directory
 
 ### Reproduce Results:
 * To reproduce the results shown in the report, please run the notebook file `Ensemble.ipynb` which is found in the `Documentation/` directory.
 
 ## More Info
- More information is found [here](http://www.cs.mun.ca/~kol/GANs-n-reels/).
- The abstract report for this project is found [here](https://github.com/vin-nag/GANs-n-reels/blob/master/Documentation/GANs%20and%20Reels_%20Abstract%20for%20CUCSC%202018.pdf).


 
 
