tabs[tabs.length-1].model = {
  text: ko.observable(),
  parse: function(data){ this.text(data); },
  save: function(){ return  this.text(); }
};
ko.applyBindings(tabs[tabs.length-1].model, $("#"+tabs[tabs.length-1].title)[0]);


