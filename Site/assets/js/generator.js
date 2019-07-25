/**
 *  This function takes care of the entire music generation process
 * @returns {Promise<void>}
 */
async function generate(){

    // load model
    const model = await tf.loadLayersModel('assets/model.json');

    // generate random noise
    const noise = Array.from({length: 100}, () => Math.random());

    // predict notes
    const prediction = model.predict(tf.tensor(noise, [1,100])).dataSync();
    let notes = Array.from(prediction);

    // scale notes using ( (note * range) + half_max_pitch )
    let scaledNotes = notes.map(scale);

    // round notes to nearest integer
    let roundedNotes = scaledNotes.map(Math.round);

    //console.log('scaled', scaledNotes);
    //console.log('rounded', roundedNotes);

    // convert notes to d major scale
    let dMajorNotes = roundedNotes.map(note_to_d_major);
    //console.log(dMajorNotes);

    // convert notes to abc string
    let myString = convertToABC(dMajorNotes);

    // render and play the song
    render(myString);
}

/**
 * This function scales the note to the range seen in the sessions
 * @param {string} string - the string representing the abc notation of the song
 * @returns {none}
 */
function render(string){
    document.getElementById("abcString").innerHTML = string;
    ABCJS.renderAbc('notation', string);
    ABCJS.renderMidi( "player", string, { qpm: 115, program: 21, generateDownload: true, hideFinishedMeasures: false});

}

/**
 * This function scales the note to the range seen in the sessions
 * @param {number} note - the real value generated by gan in range of 0 and 1
 * @returns {number} the scaled value in range of 57 to 80
 */
function scale(note){
    let note_min = 53;
    let note_max = 93;
    let half_max_pitch = Math.floor((note_max + note_min) / 2);
    let pitch_range = note_max - half_max_pitch;
    return  (note * pitch_range) + half_max_pitch;
}


/**
 * This function forces a note to be in the D Major scale
 * @param {number} note - a real valued scaled note
 * @returns {number} - a note in the scale of D Major
 */
function note_to_d_major(note){
    const d_maj_values = [2,4,6,7,9,11,13];
    let octave = Math.floor(note / 12);
    let noteInScale = note % 12;
    let noteDistances = d_maj_values.map( function(value) {
        return Math.abs(value - noteInScale);
    });
    let roundedNote = d_maj_values[argMin(noteDistances)];
    return roundedNote + 12*octave;
}

/**
 * This function gives the index of the smallest value in an array using map-reduce method
 * @param array
 * @returns {*} - the smallest lexicographical value in the array
 */
function argMin(array) {
    return array.map((x, i) => [x, i]).reduce((r,a) => (a[0] > r[0] ? r : a))[1];
}

/**
 * This method converts each midi note to the correspoding abc string
 * @param {number} note - a midi note in D major scale
 * @returns {string} the corresponding note string
 */
function convertNoteToABC(note){
    const noteToABC = {
            54: 'F,',
            55: 'G,',
            57: 'A,',
            59: 'B,',
            61: 'C,',
            62: 'D',
            64: 'E',
            66: 'F',
            67: 'G',
            69: 'A',
            71: 'B',
            73: 'C',
            74: 'd',
            76: 'e',
            78: 'f',
            79: 'g',
            81: 'a',
            83: 'b',
            85: 'c',
            86: 'd\'',
            88: 'e\'',
            90: 'f\''
        };
    return noteToABC[note];
};

/**
 * This function converts a sequence of midi notes to the corresponding abc string
 * @param {array} song - an array of midi notes
 * @returns {string} the corresponding abc string
 */
function convertToABC(song){

    // do a first pass converting all midi notes to corresponding chars
    let firstPass = song.map(convertNoteToABC);

    // split the chars to 16 notes per bar and 16 bars
    var splitBars = [];
    while(firstPass.length) splitBars.push(firstPass.splice(0,4));

    // go over each bar converting multiple occurrences of string to a number (i.e. eefff = e2 f3)
    let newArray = [];
    for (let eachBar of splitBars){
        let temp = eachBar[0];
        let occurences = 1;
        let barString = "";

        for (let x = 1; x < eachBar.length; x++){
            if (x === eachBar.length - 1){
                if (temp === eachBar[x]){
                    occurences += 1;
                    barString += temp + occurences;
                }
                else {
                    if (occurences > 1){
                        barString += temp + occurences + eachBar[x];
                    }
                    else {
                        barString += temp + eachBar[x];
                    }
                }
            }
            else if (temp !== eachBar[x]){
                if (occurences > 1){
                    barString += temp + occurences;
                }
                else {
                    barString += temp;
                }
                temp = eachBar[x];
                occurences = 1;
            }
            else {
                occurences += 1;
            }
        }
        newArray.push(barString);
    }

    var barArray = [];
    for (let i = 0; i < newArray.length; i += 4){
        let str = newArray[i];
        barArray.push([str.concat(newArray[i+1], newArray[i+2], newArray[i+3])])
    }
    // add it to the abc string
    var abcString = `T: GAN Morrison Generated\n` +
                    `C: GANs n Reels\n` +
                    `M: 4/4\n` +
                    `L: 1/16\n` +
                    `K: Dmaj\n` +
                    `|${barArray[0]}|${barArray[1]}|${barArray[2]}|${barArray[3]}|\n` +
                    `|${barArray[4]}|${barArray[5]}|${barArray[6]}|${barArray[7]}|\n` +
                    `|${barArray[8]}|${barArray[9]}|${barArray[10]}|${barArray[11]}|\n` +
                    `${barArray[12]}|${barArray[13]}|${barArray[14]}|${barArray[15]}|`;

    return abcString
}

function download() {
    var filename = "abc_notation.txt";
    var element = document.createElement('a');
    var text = document.getElementById("abcString").innerHTML;
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}
