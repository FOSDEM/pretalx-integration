Pretalx Postgres audit log
==========================

This is a plugin for `pretalx`_. It will log changes to the database using triggers. It actually applies [django-pghistory](https://django-pghistory.readthedocs.io/) to pretalx.

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-auditlog``.

3. Activate the virtual environment you use for pretalx development.

4. Execute ``pip install -e .`` within this directory to register this application with pretalx's plugin registry. Also install `pip install django-pghistory==2.8.0`

5. This is important: you need a custom settings file in order for the module to capture which user makes changes and to install apps. This is currently not configurable in other means. 
   Add a file eg auditlog_settings.py on the same location as settings.py

```
from .settings import *

INSTALLED_APPS += ["pghistory", "pgtrigger"]

MIDDLEWARE += ["pghistory.middleware.HistoryMiddleware"]

import pghistory

PGHISTORY_OBJ_FIELD = pghistory.ObjForeignKey(
    related_name="log_events", related_query_name="log_events"
)
```
6. For a dev install run `DJANGO_SETTINGS_MODULE=pretalx.auditlog_settings python -m pretalx runserver` . For another install, make sure this environmental variable is also set.

7. Admins (table user_person, field is_administrator ) will be able to see a summary of changes in /p/changelog. Note that view show a lot of data which normally is only visible to people consulting the database directly. Be mindful who you make admin.


License
-------

Copyright 2023 Johan Van de Wauw

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
