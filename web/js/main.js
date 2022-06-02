
eel.expose(play_sound, "play_sound")
function play_sound(url) {
  var audio = new Audio(url);
  audio.play();
  delete audio;
}

eel.expose(prompt_alerts, "prompt_alerts");
function prompt_alerts(description) {
    alert(description);
}

function ensureMinimumWindowSize(width, height) {
    var tooThin = (width > window.innerWidth);
    var tooShort = (height > window.innerHeight);

    if (tooThin || tooShort) {
        var deltaWidth = window.outerWidth - window.innerWidth;
        var deltaHeight = window.outerHeight - window.innerHeight;

        width = tooThin ? width + deltaWidth : window.outerWidth;
        height = tooShort ? height + deltaHeight : window.outerHeight;

        // Edge not reporting window outer size correctly
        if (/Edge/i.test(navigator.userAgent)) {
            width -= 16;
            height -= 8;
        }

        window.resizeTo(width, height);
    }
}

eel.expose(redirect,"redirect");
function redirect(url){
    window.location = url;
}

var resizeTimer;
window.addEventListener('resize', function(event) {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
        ensureMinimumWindowSize(600, 600);
    }, 250);
}, false);
