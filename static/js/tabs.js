$(document).ready(function(){
   $('.tab-enable').click(function(){
       var me = this;
       $.get('/visit/tab/enable', {id: $(me).attr('data-id')});
   });
});