function sendJSONXMLHTTPRequest(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState==4) {
            try {
                if (xhr.status==200) {
                  var parsed = JSON.parse(xhr.responseText);
                  //var parsed = xhr.responseText;
                  callback(parsed);
                }
            }
            catch(e) {
                alert('Error: ' + e.name);
            }
        }
    };
    xhr.open("GET",url);
    //xhr.setRequestHeader("Content-Type","application/json");
    xhr.setRequestHeader("Accept","application/json");
    xhr.send(null);
}

function handleGithubJSON(parsedText) {
  var template = document.getElementById("git_template");
  var stream = document.getElementById('git_stream');
  for (var i = parsedText.length-1; i >= 0; i--) {
    var newGit = template.content.cloneNode(true).childNodes[1];
    newGit.getElementsByClassName('title')[0].innerHTML = parsedText[i].repo.name + ': ' + parsedText[i].type
    newGit.getElementsByClassName('creator')[0].innerHTML = 'By ' + parsedText[i].actor.display_login + ' on ' + parsedText[i].created_at
    stream.insertBefore(newGit,stream.childNodes[0]);
  }
}

function parseGithubURL(url) {
  var username = url.replace('https://github.com/','')
  return 'https://api.github.com/users/' + username + '/events/public';
}
