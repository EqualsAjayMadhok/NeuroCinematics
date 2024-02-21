
let startSDK, stopSDK;
let registers = [];
let tries = 0;

function adjustVideoSize() {
    var windowHeight = $(window).height();
    var otherElementsHeight = $('h1').outerHeight(true) + $('p').outerHeight(true) + $('.video-controls').outerHeight(true) + $('.webcam-permission-message').outerHeight(true);
    var availableHeight = windowHeight - otherElementsHeight - 20;
    
    var videoPlayer = $('#videoPlayer');
    var webcamPreview = $('#webcamPreview');

    // Set the maximum height for the videos
    videoPlayer.css('max-height', availableHeight + 'px');
    webcamPreview.css('max-height', availableHeight + 'px');

    // Set the maximum width for the videos (90% of the viewport width)
    var maxWidth = $(window).width() * 0.9;
    videoPlayer.css('max-width', maxWidth + 'px');
    webcamPreview.css('max-width', maxWidth + 'px');

    // Preserve the aspect ratio
    var aspectRatio = videoPlayer.get(0).videoWidth / videoPlayer.get(0).videoHeight;
    var actualWidth = Math.min(maxWidth, availableHeight * aspectRatio);
    videoPlayer.css({ width: actualWidth + 'px', height: (actualWidth / aspectRatio) + 'px' });
    webcamPreview.css({ width: actualWidth + 'px', height: (actualWidth / aspectRatio) + 'px' });
}

// Adjust video size when the window is resized
$(window).resize(adjustVideoSize);


$(window).on('load', function () {
    adjustVideoSize();

    var video = $('#videoPlayer')[0];
    var playPauseBtn = $('#playPauseBtn');
    var volumeControl = $('#volumeControl');
    var fullscreenBtn = $('#fullscreenBtn');
    var requestWebcamBtn = $('#requestWebcamBtn');

    askPermission();
    requestWebcamBtn.click(function () {
        // Request access to the webcam
        askPermission();
    });

    // Play/Pause Toggle
    playPauseBtn.click(function () {
        hideCameraPreview(); // hide calibration preview
        if (video.paused) {
            startSDK();
            video.play();
            playPauseBtn.html('<i class="fas fa-pause"></i>');
        } else {
            pausePlay();
        }
    });

    // Update play button icon on video play/pause
    $(video).on('play', function () { playPauseBtn.html('<i class="fas fa-pause"></i>'); });
    $(video).on('pause', function () { playPauseBtn.html('<i class="fas fa-play"></i>'); });

    // Volume Control
    video.volume = 1;
    volumeControl.on('input', function () {
        video.volume = volumeControl.val();
    });

    // Fullscreen Toggle
    fullscreenBtn.click(function () {
        if (video.requestFullscreen) {
            video.requestFullscreen();
        } else if (video.webkitRequestFullscreen) { /* Safari */
            video.webkitRequestFullscreen();
        } else if (video.msRequestFullscreen) { /* IE11 */
            video.msRequestFullscreen();
        }
    });

    video.addEventListener('ended', function () {
        // This function is called when the video ends
        console.log('Video has ended!');
        stopSDK();
        $('#promptModal').show();
    });

    $('#submitFeedback').click(function () {
        // Validate input
        var wouldBuy = $('#wouldBuyInput').val();
        var amountToBuy = $('#amountToBuyInput').val();
        if (wouldBuy === "" || amountToBuy === "") {
            alert("Please fill in all the fields.");
            return;
        }

        // Add feedback to registers
        registers.push({
            would_buy: wouldBuy,
            amount_to_buy: amountToBuy
        });

        // Hide the modal
        $('#promptModal').hide();

        // Now call sendRegisterData
        sendRegisterData();
    });
});

$(document).ready(function() {
    // When the selection changes for wouldBuyInput
    $('#wouldBuyInput').change(function() {
        if ($(this).val() === 'false') {
            // Set amountToBuyInput to 0 if "No" is selected
            $('#amountToBuyInput').val(0);
        }
    });

    // When the value of amountToBuyInput changes
    $('#amountToBuyInput').on('input', function() {
        if ($(this).val() !== '0' && $(this).val() !== '') {
            // Set wouldBuyInput to "Yes" if any value other than 0 is entered
            $('#wouldBuyInput').val('true');
        }
    });
});


function showCameraPreview(stream) {
    var webcamPreview = $('#webcamPreview');
    webcamPreview.show();
    $("#calibrationText").show();
    webcamPreview[0].srcObject = stream;
}

function hideCameraPreview() {
    var webcamPreview = $('#webcamPreview')[0];
    $("#calibrationText").hide();
    $('#webcamPreview').hide();
    // Stop the webcam preview
    if (webcamPreview.srcObject) {
        webcamPreview.srcObject.getTracks().forEach(track => track.stop());
        webcamPreview.srcObject = null;
    }
}

function askPermission() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            document.getElementById("webcamRequiredMsg").innerText = "Loading...";
            $("#requestWebcamBtn").hide();
            showCameraPreview(stream); // Show calibration preview
            activateDetector();
        });
}

function activateDetector() {
    var video = $('#videoPlayer')[0];
    const dconfig = { maxInputFrameSize: 640, smoothness: 0.9 };
    const econfig = { smoothness: 0.25 };
    CY.loader()
        .licenseKey("4b85d2d6832cc091b3500376d6559689d9308b6b7238")
        .addModule(CY.modules().FACE_DETECTOR.name, dconfig)
        .addModule(CY.modules().FACE_EMOTION.name, econfig)
        .addModule(CY.modules().FACE_ATTENTION.name)
        .maxInputFrameSize(640)
        .load()
        .then(({ start, stop }) => {
            startSDK = start;
            stopSDK = stop;
            removeAskPermission();
            adjustVideoSize();
        });

    window.addEventListener(CY.modules().EVENT_BARRIER.eventName, (evt) => {
        const prevTime = registers.length == 0 ? -1 : Math.floor(registers[registers.length - 1].playback_timestamp / 0.25);
        const thisTime = Math.floor(video.currentTime / 0.25);
        if (evt.detail.face_detector.totalFaces == 0) {
            if (++tries == 5) {
                pausePlay();
                window.alert("No face was detected. Please, watch the clip in front of your webcam.");
            }
        }
        else {
            tries = 0;
        }
        if (evt.detail.face_detector.totalFaces > 1) {
            pausePlay();
            window.alert("Too many people on camera. Please, watch the clip by yourself.");
        }
        else if (typeof evt.detail.face_emotion !== "undefined" && evt.detail.face_emotion.dominantEmotion != undefined && prevTime != thisTime) {
            console.log('Events barrier result', video.currentTime, evt.detail.face_emotion.dominantEmotion, evt.detail.face_attention.attention, evt.detail.face_emotion.emotion[evt.detail.face_emotion.dominantEmotion]);
            addRegisterData(video.currentTime, evt.detail.face_emotion.dominantEmotion, evt.detail.face_attention.attention, evt.detail.face_emotion.emotion[evt.detail.face_emotion.dominantEmotion])
        }
    });
}

function removeAskPermission() {
    var webcamMessage = $('#webcamPermissionMessage');
    var playPauseBtn = $('#playPauseBtn');
    var fullscreenBtn = $('#fullscreenBtn');
    webcamMessage.hide();      // Hide the webcam request message
    playPauseBtn.prop('disabled', false);
    playPauseBtn.removeClass('disabled');
    fullscreenBtn.prop('disabled', false);
    fullscreenBtn.removeClass('disabled');
}

function pausePlay() {
    var video = $('#videoPlayer')[0];
    var playPauseBtn = $('#playPauseBtn');
    stopSDK();
    video.pause();
    playPauseBtn.html('<i class="fas fa-play"></i>');
}

function addRegisterData(playbackTimestamp, dominantEmotion, attention, emotionIntensity) {
    registers.push({
        playback_timestamp: playbackTimestamp,
        dominant_emotion: dominantEmotion,
        attention: attention,
        emotionIntensity: emotionIntensity
    });
}

function sendRegisterData() {
    document.getElementById('loadingScreen').style.display = 'flex';

    let dataToSend = {
        visualizationId: visualizationId,
        registers: registers
    };

    $.ajax({
        url: registerDataURL,  // URL to your Django view
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(dataToSend),
        success: function (response) {
            console.log("Data sent successfully");
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
            }
        },
        error: function (error) {
            console.error("Error sending data", error);
            // Handle errors
        }
    });
}
