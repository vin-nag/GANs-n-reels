async function generate() {
    const model = await tf.loadLayersModel('assets/model.json');
    const noise = Array.from({length: 100}, () => Math.random());
    const prediction = model.predict(tf.tensor(noise, [1,100])).dataSync();
    console.log(prediction);
    document.getElementById("play").innerHTML = prediction[0];
}

function decode(){};

function convertToABC(){};

