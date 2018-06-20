from keras import layers
from keras import optimizers
from keras import models
from keras.layers.advanced_activations import LeakyReLU

class GAN():
    def __init__(self):
        self.img_dim = [4 + 1, 64 + (4 * 2)]  # RHS of sum is padding
        self.channels = 1
        self.img_shape = [*self.img_dim, self.channels]
        self.noise_shape = [100, ]

        self.gloss = []
        self.dloss = []
        self.intervals = []
        self.graphInterval = 50

        optimizer = optimizers.Adam(0.0002, 0.5)

        self.discriminator = self.build_discriminator()
        self.discriminator.compile(loss='binary_crossentropy',
                                   optimizer=optimizer,
                                   metrics=['accuracy'])

        self.generator = self.build_generator()

        noise = layers.Input(shape=self.noise_shape)
        img = self.generator(noise)

        self.discriminator.trainable = False

        valid = self.discriminator(img)

        self.combined = models.Model(inputs=noise, outputs=valid)
        self.combined.compile(loss='binary_crossentropy', optimizer=optimizer)

    def build_generator(self, momentum=0.8, alpha_leak=0.2):
        noise_shape = self.noise_shape

        model = models.Sequential()

        model.add(layers.Dense(1024, input_shape=noise_shape))
        model.add(LeakyReLU(alpha=alpha_leak))
        model.add(layers.BatchNormalization(momentum=momentum))

        model.add(layers.Dense(64 * (1 + self.img_dim[0] // 2) * (
                    self.img_dim[1] // 2)))  # 64 filters, each of half the size of the input image
        model.add(LeakyReLU(alpha=alpha_leak))
        model.add(layers.BatchNormalization(momentum=momentum))
        model.add(layers.Reshape([(1 + self.img_dim[0] // 2), (self.img_dim[1] // 2), 64]))

        model.add(layers.Conv2DTranspose(32, [2, 5], padding="same"))  # 32 filters, each of the size of the input image
        model.add(LeakyReLU(alpha=alpha_leak))
        model.add(layers.BatchNormalization(momentum=momentum))
        model.add(layers.UpSampling2D(
            size=[2, 2]))  # now the filters are of the full size of the image, with 1 additional row at the top
        model.add(layers.Cropping2D(cropping=[[1, 0], [0, 0]]))  # remove extra padding at the top

        model.add(layers.Conv2DTranspose(1, [2, 5], padding="same", activation="tanh"))  # image

        model.summary()

        noise = layers.Input(shape=noise_shape)
        img = model(noise)

        return models.Model(noise, img)

    def build_discriminator(self, alpha_leak=0.2):
        img_shape = self.img_shape

        model = models.Sequential()

        model.add(layers.Conv2D(32, [2, 9], strides=[1, 1], padding="valid", input_shape=img_shape))
        model.add(layers.Cropping2D(cropping=[[0, 1], [4, 4]]))
        model.add(LeakyReLU(alpha=alpha_leak))
        model.add(layers.Conv2D(64, [2, 9], strides=[2, 2], padding="same"))
        model.add(LeakyReLU(alpha=alpha_leak))
        model.add(layers.Flatten())
        model.add(layers.Dense(1024))
        model.add(LeakyReLU(alpha=alpha_leak))
        model.add(layers.Dense(1, activation="sigmoid"))

        model.summary()

        img = layers.Input(shape=img_shape)
        validity = model(img)

        return models.Model(img, validity)

    def train(self, iterations, batch_size=60, sample_interval=750):
        X_train = paddedData
        halfMaxPitch = (80 + 53) // 2
        pitchRange = 80 - halfMaxPitch
        X_train = (X_train.astype(np.float32) - halfMaxPitch) / pitchRange
        X_train = np.expand_dims(X_train, axis=3)

        for iteration in range(iterations + 1):
            for _ in range(1):  # train discriminator more times
                discriminator_loss = self.train_discriminator(X_train, batch_size=batch_size)

            generator_loss = self.train_generator(batch_size)

            if (iteration % self.graphInterval):
                self.dloss.append(discriminator_loss[0])
                self.gloss.append(generator_loss)
                self.intervals.append(iteration)

            if iteration % sample_interval == 0:
                print("{} [D loss: {}, acc.: {:.2f}%] [G loss: {}]".format(
                    iteration,
                    discriminator_loss[0],
                    100 * discriminator_loss[1],
                    generator_loss))
                self.sample_images()

        # self.plotLossHistory()

    def train_discriminator(self, X_real, batch_size):
        half_batch = batch_size // 2

        discriminator_indices = np.random.randint(0, X_real.shape[0], half_batch)
        discriminator_train_imgs = X_real[discriminator_indices]

        noise = np.random.normal(0, 1, [half_batch, 100])
        generated_imgs = self.generator.predict(noise)

        discriminator_loss_real = self.discriminator.train_on_batch(discriminator_train_imgs, np.ones([half_batch, 1]))
        discriminator_loss_gen = self.discriminator.train_on_batch(generated_imgs, np.zeros([half_batch, 1]))
        # average the two losses
        discriminator_loss = np.add(discriminator_loss_real, discriminator_loss_gen) / 2

        return discriminator_loss

    def train_generator(self, batch_size):
        noise = np.random.normal(0, 1, [batch_size, 100])
        valid_y = np.array([1] * batch_size)  # move generator towards desired validity

        generator_loss = self.combined.train_on_batch(noise, valid_y)
        return generator_loss

    def plotLossHistory(self):
        plt.plot(self.intervals, self.dloss)
        plt.plot(self.intervals, self.gloss)
        plt.legend(["Discriminator Loss", "Generator Loss"])
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.ylim(ymin=0, ymax=5)
        plt.show()

    def sample_images(self):
        rows, columns = 4, 4
        noise = np.random.normal(0, 1, [rows * columns, 100])

        generated_imgs = self.generator.predict(noise)[:, :-1, 4:-4]
        generated_imgs = 0.5 * generated_imgs + 0.5

        random_real_indices = np.random.randint(0, data.shape[0], rows * columns)
        real_imgs = data[random_real_indices]

        print("Real")
        fig, axs = plt.subplots(rows, columns)
        for row in range(rows):
            for column in range(columns):
                count = row * columns + column
                axs[row, column].imshow(real_imgs[count, :, :], cmap='gray', aspect='auto')
                axs[row, column].axis('off')

        plt.show()

        print("Generated")
        fig, axs = plt.subplots(rows, columns)
        for row in range(rows):
            for column in range(columns):
                count = row * columns + column
                axs[row, column].imshow(generated_imgs[count, :, :, 0], cmap='gray', aspect='auto')
                axs[row, column].axis('off')

        plt.show()
        self.plotLossHistory()

