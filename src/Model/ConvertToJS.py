import tensorflowjs as tfjs
import tensorflow as tf

file_name = './Trained/generator_Aug10.h5'
gen_model = tf.keras.models.load_model(file_name)

tfjs.converters.save_keras_model(gen_model, './Trained')
print('done')
