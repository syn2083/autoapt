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

ws.onopen = function(){
  $message.attr("class", 'label label-info');
  $message.text('checking');
};
ws.onmessage = function(ev){
  $message.attr("class", 'label label-info');
  $message.hide();
  $message.fadeIn("slow");
  $message.text('recieved message');
  var json = JSON.parse(ev.data);
  $('#' + json.id).hide();
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
  $message.attr("class", 'label label-important');
  $message.text('closed');
};
ws.onerror = function(ev){
  $message.attr("class", 'label label-warning');
  $message.text('error occurred');
};
