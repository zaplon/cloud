var filtersModel = {

};

$(document).ready(function(){
   $('.selectpicker').selectpicker();
   ko.applyBindings(filtersModel, $('#calendar-filters')[0]);
});