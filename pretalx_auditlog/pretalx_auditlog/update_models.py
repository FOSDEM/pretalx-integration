# this is a special file - it will regenerate the models.py file - which in turn
# will be converted to migrations when you run ./manage.py makemigrations pretalx_auditlog
# you should not run it blindly but

import inspect

import pretalx.submission.models as submission_models
import pretalx.common.models as common_models
import pretalx.event.models as event_models
import pretalx.mail.models as mail_models
import pretalx.person.models as person_models
import pretalx.schedule.models as schedule_models

from django.db import models

template = """
@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete())
class {0}Proxy({0}):
    class Meta:
        proxy=True
"""



for i in [submission_models, common_models, mail_models, event_models]:
    items = list(inspect.getmembers(i, inspect.isclass))
    for item in items:
        if issubclass(item[1], models.Model):
            print(template.format(item[0]))

