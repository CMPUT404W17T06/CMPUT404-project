
function textToImage(contentType, content, replaceId) {
  var image = new Image();
  image.src = "data:" + contentType + "," + content;
  document.getElementById(replaceId).replaceWith(image);
}

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

function handleForm(post) {
  var form = $("#post_form");
  var path = '/dash/manager/edit/'+post['id'].split("/posts/")[1]
  form.find("form").attr('action',path);
  form.find("#id_title").val(post['title']);
  form.find("#id_description").val(post['description']);
  form.find("#id_contentType").val(post['contentType']);
  form.find("#id_content").val(post['content']);
  form.find("#id_categories").val(post['categories'].join());
  form.find("#id_visibility").val(post['visibility']);
  if (post['unlisted']) {
    form.find("#id_visibility").val("UNLISTED");
  }
  //form.find("#id_unlisted").prop('checked', post['unlisted']);
  form.find("#id_visibleTo").val(post['visibleTo'].join());
  form.find("#id_post_id").val(post['id']);
  form.modal();
}

function editPost(post_id) {
  url = post_id.replace('/posts/','/dash/manager/edit/')
  sendJSONXMLHTTPRequest(url,handleForm)
}


$( document ).ready(function() {
    var markdownText = document.getElementsByClassName('text/markdown');
    for (var i = 0; i < markdownText.length; ++i) {
      var item = markdownText[i];
      var converter = new showdown.Converter();
      var html = converter.makeHtml(item.innerHTML);
      item.innerHTML = html;
    }
    /*
    var dateObjects = document.getElementsByClassName('date');
    for (var i = 0; i < dateObjects.length; ++i) {
      var item = dateObjects[i];
      var date = new Date(item.innerHTML);
      //http://stackoverflow.com/a/18648314
      var locale = "en-us";
      var dateString = date.toLocaleString(locale, { month: "long" }) + ' ' + date.getUTCDate() +', ' + date.getUTCFullYear();
      item.innerHTML = dateString;
    }
    */
  }

)
