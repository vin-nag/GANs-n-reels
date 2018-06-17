# GANs and Reels
*Creating Music Using a Generative Adversarial Network*

Billard, Mitchell; Bishop, Robert; Graves, Caleb; Elsisy, Moustafa; Nagisetty, Vineel; and Northcott, Zachary: All undergraduate students at Memorial University of Newfoundland

## Motivation:
Our research aims to discover if successful AI image generative models can also be used to generate music.  We plan to use a Generative Adversarial Network, a particular type of Artificial Neural Network, in an attempt to generate Irish music.

Irish music, as one of the primary influences on traditional Newfoundland music, tends toward straightforward melodies with a fixed format. It is a style intended to be played with a single instrument by amateur musicians, resulting in notation that is simple and easy to follow. These unique qualities are the primary motivation for choosing Irish music as our target.

## Background and Related Work:
An Artificial Neural Network, or ANN, is based on a collection of connected units called nodes. These nodes can be loosely compared to neurons in the human brain with respect to their interconnectedness and influence on their neighbors. There are various types of ANNs, many of which have been successfully used to classify, predict, and generate different types of data. Recently, a UK-based team has used a Recurrent Neural Network (RNN) to generate music, and another team from Google Brain has generated music using a Long-Short Term Memory RNN. An important fact to consider is that these two models do not generate music from random noise;  they generate music from a small sequence of notes, and ‘predict’ what should come next. 

A Generative Adversarial Network, or a GAN, is an ANN consisting of a Generator that generates data when fed noise, and a Discriminator which classifies data. A common analogy is the Generator is akin to an art forger, while the Discriminator is like a detective. The analogy is useful as, after being trained, the Generator can be used to create original ‘art’. GANs have worked well with pictures, but to our knowledge there has not been a successful attempt to generate music using GANs. 

## Research Approach:
We hope to use the distinctive structure of Irish tunes to make them suitable for GAN-based music generation. Our main idea is to regard an Irish melody as a fixed-size object with cross-references among its parts:  “music as a picture” view.  The two key components of this project are:

* Preprocessing: 
  * Creating a well-defined format for music encoding suitable for GANs
  * Representing “vertical” dependencies in the tunes
* Modifying GANs for improved performance via:
  * Statistical “Bagging” and “Boosting” to mimic the full input distribution
  * Modifying training rate to avoid “Mode Collapse”	

## Novelty:
Though there are RNN-based Irish music generators, we found no GANs which successfully generated music. Unlike RNNs,  GANs could truly generate music from scratch,  rather than using prediction. To our knowledge, no one has presented the idea of organizing music like a picture, which makes our encoding unique.

## Results and Contributions:
Our code and the results will be uploaded to an online repository for public access [here:](https://github.com/vin-nag/GANs-n-reels)

