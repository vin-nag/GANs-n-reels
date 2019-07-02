const model = tf.loadLayersModel('/home/vineel/PycharmProjects/GANs-n-reels/src/Model/Trained/model.json');

// randomly generated N = 40 length array 0 <= A[N] <= 39
const noise = Array.from({length: 100}, () => Math.random() );

console.log(noise);