# this is a special file - it will regenerate the models.py file - which in turn
# will be converted to migrations when you run ./manage.py makemigrations pretalx_auditlog

template = """
@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete())
class {0}Proxy({0}):
    class Meta:
        proxy=True
"""

print(template.format("Room"))

from modulefinder import ModuleFinder

finder = ModuleFinder()

print(inspect.getmembers(submission_models))
