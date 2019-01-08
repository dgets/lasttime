getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', url, true);
    xhr.responseType = 'json';

    xhr.onload = function() {
      var status = xhr.status;

      if (status === 200) {
        callback(null, xhr.response);
      } else {
        callback(status, xhr.response);
      }

    };

    xhr.send();
};

function secondsToHms(d) {
    d = Number(d);

    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    return ('0' + h).slice(-2) + ":" + ('0' + m).slice(-2) + ":" + ('0' + s).slice(-2);
}

