var video = document.querySelector("#video-window");

$(document).ready(function () {

    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;

    key('space', 'ENDOSCOPE', function (event) {
        event.preventDefault();
        endoscope.takeScreenShot();
        return;
    });
    key('v', 'ENDOSCOPE', function (event) {
        event.preventDefault();
        endoscope.hideVideo();
        if ($('#capture-video-stop').is(":visible"))
            endoscope.stopVideo();
        else
            endoscope.captureVideo();
        return;
    });

    if (navigator.getUserMedia) {
        navigator.getUserMedia({video: true}, handleVideo, videoError);
    }

    function handleVideo(stream) {
        video.src = window.URL.createObjectURL(stream);
        endoscope.localMediaStream = stream;
    }

    function videoError(e) {
        // do something
    }

    key.setScope('ENDOSCOPE');
    console.log('scope');
});

var endoscope = {
    slidesShow: ko.observable(false),
    videosShow: ko.observable(false),
    isRecording: ko.observable(false),
    slides: ko.observable([0, 0]),
    videos: ko.observable([0, 0]),
    canvas: document.querySelector('canvas'),
    ctx: document.querySelector('canvas').getContext('2d'),
    width: 640,
    height: 480,
    blinkScreen: function () {
        $('#effects-canvas').css('z-index', endoscope.slides()[0] + 2);
        $('#effects-canvas').css('display', 'block');

        $('#effects-canvas').animate({
            opacity: 0.75
        }, 250, function () {
            $(this).animate({
                opacity: 0
            }, 250, function () {
                $('#effects-canvas').css('display', 'none');
            })
        });

    },
    recordVideo: function(){
        this.isRecording(!this.isRecording());
    },
    showVideos: function(){
        this.videosShow(!this.videosShow());
    },
    showSlides: function(){
        this.slidesShow(!this.slidesShow());
    },
    takeScreenShot: function(){
        if (endoscope.localMediaStream) {
            endoscope.ctx.drawImage(video, 0, 0, endoscope.width, endoscope.height);
            endoscope.blinkScreen();
            var image = endoscope.canvas.toDataURL('image/jpg');
            endoscope.slides.push({src: image});
        }
    },
    drawVideoFrame: function (time) {
        endoscope.rafId = requestAnimationFrame(endoscope.drawVideoFrame);
        endoscope.ctx.drawImage(video, 0, 0, endoscope.width, endoscope.height);
        endoscope.frames.push(canvas.toDataURL('image/webp', 0.75));
    }
};
ko.applyBindings(endoscope, $('#video-container')[0]);


function xhr(url, data, callback) {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (request.readyState == 4 && request.status == 200) {
            callback(request.responseText);
        }
    };
    request.open('POST', url);
    request.send(data);
};
