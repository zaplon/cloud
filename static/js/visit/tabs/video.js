var video = document.querySelector("#endoscope-video");

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

var playSound = false;
endoscope = {
    rafId: '',
    slideNr: $('.endoscope-slide').length,
    localMediaStream: null,
    video: document.querySelector('video'),
    canvas: document.querySelector('canvas'),
    ctx: this.canvas.getContext('2d'),
    frames: [],
    height: 480,
    width: 640,
    videosCount: $('.endoscope-video').length,
    currentVideo: 1,
    videoData: [],
    streaming: false,
    slidesHidden: true,
    showSlides: function () {
        if (endoscope.slidesHidden) {

            $('#recorded-video').hide();
            $('#hide-video').hide();
            $('#upload-video').hide();

            var slider = $('#pictures-slider');
            var video = $('video#endoscope-video');
            //slider.children().each(function(i,el){
            //   $(el).css('z-index', parseInt($(el).css('z-index')) + 100);
            //});
            $('#effects-canvas').css('display', 'none');
            $(video).css('display', 'none');
            if (endoscope.slideNr > 0) {
                $('#endoscope-templates').css('display', 'block');
            }
            endoscope.flipSlides();
            $('#slide-number').html('1/' + (endoscope.slideNr));
            $('#slide-number').attr('data-number', 1);
            $(slider).css('display', 'block');
            $(this).html('Podgląd kamery');
            if (endoscope.slideNr == 0)
                $('.slide-control').hide();
            else
                $('.slide-control').show();

        }
        else {
            var slider = $('#pictures-slider');
            var video = $('video');
            //slider.children().each(function(i,el){
            //   $(el).css('z-index', parseInt($(el).css('z-index')) - 100);
            //});
            $(video).css('display', 'block');
            $(slider).css('display', 'none');
            $('#endoscope-templates').css('display', 'none');
            $(this).html('Wybierz zdjęcia');
        }
        endoscope.slidesHidden = !endoscope.slidesHidden;
    },
    temporarySave: function (data) {
        $.post('addPicture', {data: data}).done(function (res) {
            res = JSON.parse(res);
            $('#slide' + (endoscope.slideNr)).attr('data-id', res.id);
            $('#slide-desc' + (endoscope.slideNr)).attr('data-id', res.id);
        });
    },
    blinkScreen: function () {
        $('#effects-canvas').css('z-index', endoscope.slideNr + 2);
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
    drawVideoFrame: function (time) {
        endoscope.rafId = requestAnimationFrame(endoscope.drawVideoFrame);
        endoscope.ctx.drawImage(video, 0, 0, endoscope.width, endoscope.height);
        endoscope.frames.push(canvas.toDataURL('image/webp', 0.75));
    },
    videoPreview: function () {
        endoscope.slidesHidden = false;
        endoscope.showSlides();
        $('#video-sign').show();
        $('#capture-video').hide();
        $('#capture-video-stop').show();
        $('#upload-video').hide();
    },
    captureVideo: function (time) {
        endoscope.frames = [];
        endoscope.videoPreview();
        endoscope.drawVideoFrame(time);
    },
    deleteVideo: function () {
        callback = function () {
            $('#recorded-video video[data-video-nr=' + endoscope.currentVideo + ']').remove();

            $('#recorded-video video').each(function (i, v) {
                var id = $(v).attr('data-video-nr');
                id = parseInt(id);
                if (id > endoscope.currentVideo)
                    $(v).attr('data-video-nr', id - 1);
            });

            endoscope.videosCount -= 1;
            if (endoscope.videosCount > 0) {
                endoscope.changeVideo(-1);
            }
            else {
                endoscope.currentVideo = 1;
                endoscope.hideVideo(true);
            }
        };
        var id = $('#recorded-video video[data-video-nr=' + endoscope.currentVideo + ']').attr('data-id');
        if (id)
            $.get('/portal/deleteAttachment/', {id: id}).success(function () {
                callback();
            }).fail(function () {
                showMessage('Przesyłanie pliku', 'Wystąpił błąd podczas usuwania nagrania!', 'file-sended');
            });
        else
            callback();
    },
    stopVideo: function () {
        $('#video-sign').hide();
        $('#capture-video').show();
        $('#capture-video-stop').hide();
        $('#show-video').show();
        cancelAnimationFrame(endoscope.rafId);  // Note: not using vendor prefixes
        // 2nd param: framerate for the video file.
        var webmBlob = Whammy.fromImageArray(endoscope.frames, 1000 / 60);
        var video = document.createElement('video');
        video.src = window.URL.createObjectURL(webmBlob);
        video.controls = true;
        video.autoplay = true;
        endoscope.videosCount += 1;
        endoscope.videoData[endoscope.videosCount] = webmBlob;
        video.setAttribute('data-video-nr', endoscope.videosCount);
        document.getElementById('recorded-video').appendChild(video);
        endoscope.uploadVideo(webmBlob);
    },
    changeVideo: function (dir) {
        endoscope.currentVideo += dir;
        if (endoscope.currentVideo < 1)
            endoscope.currentVideo = endoscope.videosCount;
        if (endoscope.currentVideo > endoscope.videosCount)
            endoscope.currentVideo = 1;
        $('#recorded-video video').hide();
        $('#video-number').html(endoscope.currentVideo + '/' + endoscope.videosCount);
        $('#recorded-video video[data-video-nr=' + endoscope.currentVideo + ']').show();
    },
    uploadVideo: function (data) {
        var fileType = 'video'; // or "audio"
        var fileName = 'ABCDEF.webm';  // or "wav" or "ogg"

        var formData = new FormData();
        formData.append(fileType + '-filename', fileName);
        if (!data)
            data = endoscope.videoData[endoscope.currentVideo];
        formData.append(fileType + '-blob', data);

        xhr('addVideo', formData, function (res) {
            st = JSON.parse(res);
            if (st.success) {
                $('#recorded-video video[data-video-nr=' + endoscope.currentVideo + ']').attr('data-id', st.id);
                //showMessage('Przesyłanie pliku', 'Plik przesłano poprawnie!', 'file-sended');
            }
            else
                showMessage('Przesyłanie pliku', 'Wystąpił błąd podczas przesyłania pliku!', 'file-sended');
        }, function () {
            showMessage('Przesyłanie pliku', 'Wystąpił błąd podczas przesyłania pliku!', 'file-sended');
        });

    },
    showVideo: function () {
        $('#capture-video').hide();
        $('#pictures-slider').hide();
        $('#recorded-video').show();
        $('#show-video').hide();
        $('#endoscope-video').hide();
        $('#hide-video').show();
        $('.slide-control').show();
        //$('#upload-video').show();
        endoscope.changeVideo(0);
    },
    hideVideo: function (NoShowVideo) {
        $('#capture-video').show();
        $('#recorded-video').hide();
        if (!NoShowVideo || endoscope.videosCount > 0)
            $('#show-video').show();
        $('#endoscope-video').show();
        $('#hide-video').hide();
        $('#upload-video').hide();
    },
    takeScreenShot: function () {
        if ($('#pictures-slider').is(":visible"))
            return;
        if (endoscope.localMediaStream) {
            endoscope.ctx.drawImage(video, 0, 0, endoscope.width, endoscope.height);
            // "image/webp" works in Chrome.
            // Other browsers will fall back to image/png.

            //if (endoscope.slidesHidden) {
            $('video').css('display', 'block');
            $('#pictures-slider').css('display', 'none');
            $('#effects-canvas').css('display', 'block');
            $('#endoscope-templates').css('display', 'none');
            //}

            $('#pictures-slider').append('<div class="endoscope-slide" style="position:absolute; z-index:' + (endoscope.slideNr + 1) + '" id="slide' + (endoscope.slideNr + 1) + '"><div style="z-index:' + (endoscope.slideNr + 1) + '" slide="' + (endoscope.slideNr + 1) + '" title="Wybierz zdjęcie" class="thick thick-selected">v</div><div style="z-index:' + (endoscope.slideNr + 1) + '" slide="' + (endoscope.slideNr + 1) + '" class="delete-slide" title="Trwale usuń zdjęcie">X</div><img width="640" height="480" /><textarea type="ENDOSCOPE" id="slide-desc' + (endoscope.slideNr + 1) + '" class="tab-textarea picture-desc"></textarea></div>');
            var image = endoscope.canvas.toDataURL('image/jpg');
            document.querySelector('#pictures-slider #slide' + (endoscope.slideNr + 1) + ' img').src = image;
            endoscope.temporarySave(image);
            endoscope.blinkScreen();
            if (playSound)
                endoscope.playSound();
            endoscope.slideNr = endoscope.slideNr + 1;
        }
    },
    playSound: function () {
        var snd = new Audio("/static/sound/ding.mp3");
        snd.play();
    },
    changeSlide: function (dir) {
        var slides = $('.endoscope-slide');
        var ind = 0;
        slides.each(function (i, el) {
            ind = parseInt($(el).css('z-index')) + dir;
            if (ind > slides.length)
                ind = 1;
            if (ind == 0)
                ind = slides.length;
            $(el).css('z-index', ind);
        });
        $('#slide-number').html(ind + '/' + (endoscope.slideNr));
        $('#slide-number').attr('data-number', ind);
    },
    flipSlides: function () {
        var slides = $('.endoscope-slide');
        var count = slides.length;
        slides.each(function (i, el) {
            $(el).css('z-index', count - i);
        });
    }
};

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

endoscope.video.addEventListener('canplay', function (ev) {
    var video = endoscope.video;
    var canvas = endoscope.canvas;
    var streaming = endoscope.streaming;
    if (!streaming) {
        height = video.videoHeight / (video.videoWidth / endoscope.width);
        video.setAttribute('width', endoscope.width);
        video.setAttribute('height', endoscope.height);
        canvas.setAttribute('width', endoscope.width);
        canvas.setAttribute('height', endoscope.height);
        streaming = true;
    }
}, false);


$('#select-pictures').click(endoscope.showSlides);
$('#capture-screen').click(endoscope.takeScreenShot);
$('#capture-video').click(endoscope.captureVideo);
$('#capture-video-stop').click(endoscope.stopVideo);
$('#show-video').click(endoscope.showVideo);
$('#hide-video').click(endoscope.hideVideo);
$('#upload-video').click(endoscope.uploadVideo);

$(window).load(function () {

    $('#collect-pictures').click(function () {
        $.get('collect-pictures').success(function () {
            window.location.reload();
        });
    });

    $('#pictures-slider .arrow').click(function () {
        if ($(this).attr('id') == 'arrow-left')
            var dir = -1;
        else
            var dir = 1;
        endoscope.changeSlide(dir);
    });
    $('#pictures-slider').delegate('.thick', 'click', function () {
        var me = $(this);
        if ($(this).hasClass('thick-selected')) {
            if ($(this).parent().attr('data-id')) {
                $.get('markPicture', {'id': me.parent().attr('data-id')}).success(function (res) {
                    me.removeClass('thick-selected');
                }).fail(function () {
                    alert('Nie udało się odznaczyć zdjęcia');
                });
            }
        }
        else {
            if ($(this).parent().attr('data-id')) {
                $.get('markPicture', {'id': me.parent().attr('data-id')}).success(function (res) {
                    me.addClass('thick-selected');
                }).fail(function () {
                    alert('Nie udało się odznaczyć zdjęcia');
                });
            }
        }
    });

    $('#pictures-slider').delegate('.picture-desc', 'focusout', function () {
        var id = $(this).attr('data-id');
        $.get('addPictureDesc', {'desc': $(this).val(), 'id': id});
    });

    $('#pictures-slider').delegate('.delete-slide', 'click', function () {
        if ($(this).parent().attr('data-id')) {
            var me = $(this);
            $.get('deletePicture', {'id': me.parent().attr('data-id')}).success(function (res) {
                me.parent().remove();
                endoscope.slideNr = endoscope.slideNr - 1;
                var nm = parseInt($('#slide-number').attr('data-number'));
                if (endoscope.slideNr == 0) {
                    $('.slide-control').hide();
                    $('#endoscope-templates').hide();
                }
                else {
                    $('.slide-control').show();
                    $('#endoscope-templates').show();
                }
                if (nm == 1) {
                    nm = 1;
                }
                else
                    nm = nm - 1;
                $('#slide-number').html((nm) + '/' + (endoscope.slideNr));
                $('#slide-number').attr('data-number', nm);
            }).fail(function () {
                alert('Nie udało się usunąć zdjęcia');
            });
        }
        else
            $(this).parent().remove();
    });


    //ustawienia filtru wideo
    var can = $('#effects-canvas');
    var pos = $('video').position();
    can.css('top', pos.top + 'px');
    can.css('left', pos.left + 'px');

    $('#no-icd10').click();

    //przesuwamy na pierwszy slajd

    key.setScope('ENDOSCOPE');
    console.log('scope');

    if (window.isKolpo)
        endoscope.showSlides();
});


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
//window.setTimeout(function(){ key.setScope('ENDOSCOPE'); },5000);

