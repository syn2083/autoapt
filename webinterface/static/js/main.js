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
