from crispy_forms.helper import FormHelper
import json
from crispy_forms.utils import render_crispy_form
from django.template.context_processors import csrf


class NoFormFormHelper(FormHelper):
    form_tag = False

    
def ajax_form_validate(data, form_class):
    data = json.loads(data)
    form = form_class(initial=data)
    if form.is_valid():
        form.save()
        return json.dumps(success=True)
    else:
        ctx = {} 
        ctx.update(csrf(request))
        form_html = render_crispy_form(form, context=ctx)
        return json.dumps({'success': False, 'form_html': form_html})

