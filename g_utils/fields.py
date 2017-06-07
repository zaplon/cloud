from django.forms.widgets import TextInput


class AutocompleteWidget(TextInput):

    def __init__(self, attrs=None, **kwargs):
        super(AutocompleteWidget, self).__init__(attrs)
        self.url = kwargs.get('url', False)
        self.display = kwargs.get('display', False)

    def render(self, name, value, attrs=None):
        if not self.url:
            raise ValueError('url is obligatory.')
        hidden_input = '<input type="hidden" name="%s" value="%s" id="id_%s">' % (name, value, name)
        name_autocomplete = name + '_autocomplete'
        attrs['id'] = 'id_' + name_autocomplete
        input_html = super(AutocompleteWidget, self).render(name_autocomplete, self.display if self.display else value, attrs)
        script = """
            <script>
                $(document).ready(function(){
                    $( "input#%s" ).autocomplete({
                      source: "%s",
                      minLength: %s,
                      select: function( event, ui ){ $('#id_%s').val(ui.item.id) }
                    }).data('ui-autocomplete')._renderItem = function( ul, item ) {
                        ul.addClass('list-group');
                        return $( "<a class='list-group-item list-group-item-action'>" )
                          .attr( "data-value", item.value )
                          .append(item.label)
                          .appendTo( ul );
                        };
                });
            </script>
                """ % ('id_'+name_autocomplete, self.url, attrs.get('minlength', 2), name)

        return hidden_input + input_html + script
