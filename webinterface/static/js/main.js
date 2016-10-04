/**
 * Created by venom on 8/19/2016.
 */
// Submit post on submit
$('#start').click(function() {
$.get('/start_demo/', function(data){
    $('#demo_status').html(data);
});
});
$('#stop').click(function() {
$.get('/stop_demo/', function(data){
    $('#demo_status').html(data);
});
});
$('#pause').click(function() {
$.get('/pause_demo/', function(data){
    $('#demo_status').html(data);
});
});
$('#reset_seed').click(function() {
$.get('/reset_seed/', function(data){
    $('#demo_status').html(data);
});
});
var ws = new WebSocket('ws://127.0.0.1:8888/ws');
var $message = $('#message');
var $control = $('#control');
var $td = $('#td');

ws.onopen = function(){
  $message.attr("class", 'tag tag-info');
  $message.text('Checking Status...');
  ws.send("status_check")

};
ws.onmessage = function(ev){
  var json = JSON.parse(ev.data);
  $('#' + json.id).hide();
  if (json.id == "message"){
    if(json.value == "Running"){
    $message.attr("class", 'tag tag-success');
    }
    else if(json.value == "Paused"){
      $message.attr("class", 'tag tag-warning');
    }
    else{
      $message.attr("class", 'tag tag-danger');
    }
  }
  else if(json.id == "td"){
    if(json.value == "Running"){
    $td.attr("class", 'tag tag-success');
    }
    else if(json.value == "Paused"){
      $td.attr("class", 'tag tag-warning');
    }
    else{
      $td.attr("class", 'tag tag-info');
    }
  }

  $('#' + json.id).fadeIn("slow");
  $('#' + json.id).text(json.value);
  var $rowid = $('#row' + json.id);
  if(json.value > 500){
    $rowid.attr("class", "error");
  }
  else if(json.value > 200){
    $rowid.attr("class", "warning");
  }
  else{
    $rowid.attr("class", "");
  }
};
ws.onclose = function(ev){
  $message.attr("class", 'tag tag-important');
  $message.text('WebSocket Closed');
};
ws.onerror = function(ev){
  $message.attr("class", 'tag tag-warning');
  $message.text('WebSocket Error');
};
