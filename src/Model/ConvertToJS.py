import tensorflowjs as tfjs
import tensorflow as tf
import numpy as np

gen_model = tf.keras.models.load_model('./Trained/generator_better.h5')
#dis_model = tf.keras.models.load_model('./Trained/discriminator.h5')

tfjs.converters.save_keras_model(gen_model, './Trained')
#tfjs.converters.save_keras_model(dis_model, './Trained')
print('done')

#noise = np.random.normal(0, 1, [1, 100]) #20 arrays of noise of shape [100,]

#print(noise)

#prediction = model.predict(noise)

#print(prediction.shape)

