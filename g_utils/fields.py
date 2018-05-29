# -*- coding: utf-8 -*-
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
        attrs['placeholder'] = attrs.get('placeholder', u'zacznij pisać...')
        input_html = super(AutocompleteWidget, self).render(name_autocomplete, self.display if self.display else value, attrs)
        script = """
            <script>
                $(document).ready(function(){
                    $( "input#%s" ).autocomplete({
                      source: "%s",
                      minLength: %s,
                      select: function( event, ui ){ $('#id_%s').val(ui.item.id) }
                    }).data('ui-autocomplete')._renderItem = function( ul, item ) {
                        ul.addClass('list-group autocomplete-list');
                        return $( "<a class='list-group-item list-group-item-action'>" )
                          .attr( "data-value", item.value )
                          .append(item.label)
                          .appendTo( ul );
                        };
                });
            </script>
                """ % ('id_'+name_autocomplete, self.url, attrs.get('minlength', 2), name)

        return hidden_input + input_html + script


class Choice(object):
    def __init__(self, value, label=None):
        self.value = value
        self.label = label or str(value)


class MetaChoicesEnum(type):
    def __new__(cls, name, bases, attrs):
        items = {}
        for base in bases:
            if isinstance(base, MetaChoicesEnum):
                items.update(base._items)

        for attribute_name, definition in attrs.items():
            if attribute_name.startswith('_'):
                continue

            if type(definition) is list or type(definition) is tuple:
                value, label = definition

            else:
                value = definition

                # Generate label
                words = [word.lower() for word in str(attribute_name).split('_')]
                words[0] = words[0].title()

                label = ' '.join(words)

            items[attribute_name] = Choice(value, label)

        attrs['_items'] = items
        return type.__new__(cls, name, bases, attrs)

    def __iter__(cls):
        return iter(cls.choices)

    def __len__(self):
        return len(self._items)

    @property
    def choices(cls):
        return [(x.value, x.label) for x in cls._items.itervalues()]

    @property
    def values(self):
        return self._items.values()


class ChoicesEnum(object):
    __metaclass__ = MetaChoicesEnum
