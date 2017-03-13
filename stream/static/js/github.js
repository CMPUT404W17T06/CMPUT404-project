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
  var stream = document.getElementById('git_events');
  if (parsedText.length < 30) {
    $('#git_button').hide();
  }
  for (var i = 0; i < parsedText.length; i++) {
    var newGit = template.content.cloneNode(true).childNodes[1];
    newGit.getElementsByClassName('title')[0].innerHTML = parsedText[i].repo.name + ': ' + parsedText[i].type
    newGit.getElementsByClassName('creator')[0].innerHTML = parsedText[i].actor.display_login
    newGit.getElementsByClassName('creation_date')[0].innerHTML = parsedText[i].created_at
    stream.append(newGit,stream.childNodes[0]);
  }
}

var username = '';
var page = 1;

function loadPage(url) {
  username = url.replace('https://github.com/','');
  var url = 'https://api.github.com/users/' + username + '/events/public?page=';
  var url_page = url + String(page)
  sendJSONXMLHTTPRequest(url_page,handleGithubJSON)
  page++;
}

/*
function parseGithubURL(url) {
  username = url.replace('https://github.com/','');
  return 'https://api.github.com/users/' + username + '/events/public';
}
*/
/*
function goThroughPages(url) {
  username = url.replace('https://github.com/','');
  var url = 'https://api.github.com/users/' + username + '/events/public?page=';
  for (var i=1; i<=10; i++) {
    var url_page = url + String(i)
    sendJSONXMLHTTPRequest(url_page,handleGithubJSON)
  }
}
*/
