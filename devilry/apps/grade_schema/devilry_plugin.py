from django.utils.translation import ugettext as _
from devilry.core import gradeplugin
from django.core.urlresolvers import reverse
from models import SchemaGradeResults
from gradeviews import view

def url_callback(assignment_id):
    return reverse('devilry.addons.grade_schema.views.edit_schema',
                args=[assignment_id])

gradeplugin.registry.register(gradeplugin.RegistryItem(
        view = view,
        model_cls = SchemaGradeResults,
        label = _('Schema - for demonstration not for production use'),
        admin_url_callback = url_callback,
        description = _('Only for demonstration and documentation purposes.')
))