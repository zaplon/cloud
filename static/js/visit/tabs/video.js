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
    endoscope.loadSlides();
});

var endoscope = {
    slidesShow: ko.observable(false),
    videosShow: ko.observable(false),
    isRecording: ko.observable(false),
    slides: ko.observableArray([]),
    videos: ko.observableArray([]),
    slideIndex: ko.observable(0),
    videoIndex: ko.observable(0),
    currentSlide: ko.observable({}),
    currentVideo: ko.observable({}),
    videos: ko.observableArray([]),
    canvas: document.querySelector('canvas'),
    ctx: document.querySelector('canvas').getContext('2d'),
    width: 640,
    height: 480,
    changeSlide: function (dir, me) {
        if (me.slidesShow()){
            var newIndex = me.slideIndex() + dir;
            var index = me.slideIndex;
            var slide = me.currentSlide;
            var slides = me.slides
        }
        else {
            var newIndex = me.videoIndex() + dir;
            var index = me.videoIndex;
            var slide = me.currentVideo;
            var slides = me.videos;
        }
        var nr = me.slides().length;
        if (newIndex < 0)
            index(nr);
        else if (newIndex >= nr)
            index(0);
        else
            index(newIndex);
        slide(slides()[index()]);
    },
    loadSlides: function () {
        var me = this;
        $.getJSON('/rest/results/', {type: 'ENDOSCOPE_IMAGE', pesel: visit.patient().pesel, endoscope: 1}, function(data){
            me.slides(data);
        });
    },
    loadVideos: function () {
        var me = this;
        $.getJSON('/rest/results/', {type: 'ENDOSCOPE_VIDEO', pesel: visit.patient().pesel, endoscope: 1}, function(data){
            me.slides(data);
        });
    },
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
            var slide = {file: image};
            endoscope.slides.push(slide);
            $.ajax({
                method: 'POST',
                data: {file: slide.file, endoscope_image: 1, visit: visit.id, patient: visit.patient().id},
                url: '/rest/results/',
                success: function(){

                },
                fail: function(){
                    notie.alert('Wystąpił błąd przy zapisywaniu zdjęcia na serwerze', 3);
                }
            });
            if (!endoscope.currentSlide().file)
                endoscope.currentSlide(slide);
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
