from django import template

from responsive_waves.models import Variable

register = template.Library()

def is_shown(variable, wave_path):
    try:
        var_options = Variable.objects.get(browser__name=wave_path,
                                           path=variable.path)
    except Variable.DoesNotExist:
        return False
    return var_options.shown

register.filter('is_shown', is_shown)

