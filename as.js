
var is_running = false;
function $(id){ return document.getElementById(id) }

function enter(){
  if( window.event.keyCode == 13 ){
  //if(!is_running){
    search('q', 'r');
  //}
  }
}

function search(q, r){
    ajax('index.cgi?action=do&q=' + gen_query(q) + '&qid=' + q + '&rid=' + r, r);
}

function google(q){
    location.href = 'http://www.google.com/#q=' + gen_query(q);
}

function rocky(q){
    location.href = 'http://www.google.com/#q=rocky';
}

function gen_query(q){
    var ids = q.split('-');
    var query = "";
    var idchain = "";
    for(var id in ids){
      if(query == ""){
        query = $(idchain + ids[id]).value;
      } else {
        query = query + '+' + $(idchain + ids[id]).value;
      }
      idchain = idchain + ids[id] + '-';
    }
    return query;
}

function ajax(url, r){
    var xmlhttp = gen_xmlhttp();

    $(r).innerHTML = '<img src="now-loading.gif" />';
    is_running = true;

    xmlhttp.open("GET", url, true);
    xmlhttp.onreadystatechange = function() {
      if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
          $(r).innerHTML = xmlhttp.responseText;
          is_running = false;
      }
    }
    xmlhttp.send("");
}

function gen_xmlhttp(){
    var xmlhttp = false;
    if(typeof ActiveXObject != "undefined"){
      try {
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
      } catch (e) {
        xmlhttp = false;
      }
    }
    if(!xmlhttp && typeof XMLHttpRequest != "undefined") {
      xmlhttp = new XMLHttpRequest();
    }
    return xmlhttp;
}
