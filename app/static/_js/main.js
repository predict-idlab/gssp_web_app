/* Copyright 2013 Chris Wilson

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

window.AudioContext = window.AudioContext || window.webkitAudioContext;

console.log('v1.0');

var audioContext = new AudioContext();
var audioInput = null,
    realAudioInput = null,
    inputPoint = null,
    audioRecorder = null;
var rafID = null;
var analyserContext = null;
var canvasWidth, canvasHeight;
var recIndex = 0;


function gotBuffers(buffers, file_id) {
    audioRecorder.exportWAV(doneEncoding);
}

function doneEncoding(soundBlob) {
    // fetch('/audio', {method: "POST", body: soundBlob}).then(response => $('#output').text(response.text()))
    // TODO -> change this hard_coded file name code
    let file_name = document.getElementById('afbeelding').src.split('/');
    file_name = file_name.slice(Math.max(file_name.length - 2, 1)).join('/').split('.')[0];
    file_name += "__" + new Date().toLocaleTimeString('nl-BE', { hour12: false });

    $.ajax({
        type: "POST",
        url: `/audio/wav/` + file_name,
        data: soundBlob,
        processData: false,
        contentType: false,
        success: function (response) {
            console.log(response)
            document.getElementById('btn_next').hidden = false;
            document.getElementById('output').innerHTML = response;
            // Do something after the sleep!
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert("AUDIO post failed with error: " + XMLHttpRequest.responseText);
        }
    })
    recIndex++;
}

function stopRecording() {
    // stop recording
    audioRecorder.stop();
    audioRecorder.getBuffers(gotBuffers);
}

function startRecording() {
    audioContext.resume()
    // start recording
    if (!audioRecorder) {
        alert("no audio recorder detected");
        initAudio();
        // warning -> no audiorecorder is selected ...
        return;
    }
    audioRecorder.clear();
    audioRecorder.record();
}

function convertToMono(input) {
    var splitter = audioContext.createChannelSplitter(2);
    var merger = audioContext.createChannelMerger(2);

    input.connect(splitter);
    splitter.connect(merger, 0, 0);
    splitter.connect(merger, 0, 1);
    return merger;
}

function cancelAnalyserUpdates() {
    window.cancelAnimationFrame(rafID);
    rafID = null;
}

function updateAnalysers(time) {
    if (!analyserContext) {
        var canvas = document.getElementById("analyser");
        canvasWidth = canvas.width;
        canvasHeight = canvas.height;
        analyserContext = canvas.getContext('2d');
    }

    // analyzer draw code here
    {
        var SPACING = 3;
        var BAR_WIDTH = 1;
        var numBars = Math.round(canvasWidth / SPACING);
        var freqByteData = new Uint8Array(analyserNode.frequencyBinCount);

        analyserNode.getByteFrequencyData(freqByteData);

        analyserContext.clearRect(0, 0, canvasWidth, canvasHeight);
        analyserContext.fillStyle = '#F6D565';
        analyserContext.lineCap = 'round';
        var multiplier = analyserNode.frequencyBinCount / numBars;

        // Draw rectangle for each frequency bin.
        for (var i = 0; i < numBars; ++i) {
            var magnitude = 0;
            var offset = Math.floor(i * multiplier);
            // gotta sum/average the block, or we miss narrow-bandwidth spikes
            for (var j = 0; j < multiplier; j++)
                magnitude += freqByteData[offset + j];
            magnitude = magnitude / multiplier;
            var magnitude2 = freqByteData[i * multiplier];
            analyserContext.fillStyle = "hsl( " + Math.round((i * 360) / numBars) + ", 100%, 50%)";
            analyserContext.fillRect(i * SPACING, canvasHeight, BAR_WIDTH, -magnitude);
        }
    }

    rafID = window.requestAnimationFrame(updateAnalysers);
}

function gotStream(stream) {
    inputPoint = audioContext.createGain();

    // Create an AudioNode from the stream.
    realAudioInput = audioContext.createMediaStreamSource(stream);
    audioInput = realAudioInput;
    audioInput.connect(inputPoint);

    audioInput = convertToMono(audioInput);

    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    inputPoint.connect(analyserNode);

    audioRecorder = new Recorder(inputPoint);

    zeroGain = audioContext.createGain();
    zeroGain.gain.value = 0.0;
    inputPoint.connect(zeroGain);
    zeroGain.connect(audioContext.destination);
    updateAnalysers();
}

function initAudio() {
    if (audioRecorder === null) {
        var constraints = {
            "audio": {
                "autoGainControl": false,
                "echoCancellation": false,
                "googAutoGainControl": false,
                "noiseSuppression": false
            },
        }
        navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
            gotStream(stream)
        }).catch(function (error) {
            console.log(error);
            alert(error);
        });
    }
}

window.addEventListener('load', initAudio);

function unpause() {
    document.getElementById('init').style.display = 'none';
    audioContext.resume().then(() => {
        console.log('Playback resumed successfully');
    });
}