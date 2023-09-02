Pretalx exporter for nanoc (FOSDEM)
===================================

This is a plugin for `pretalx`_ that builds a yaml file that can be consumed by the `fosdem website`_ nanoc build.

Note this is a first version/proof of concept. Bug reports and pull requests are highly appreciated.

Features not yet implemented are:
* attachments and links
* ordering of tracks (may need a change/plugin in pretalx?)
* track type (eg main track/keynote)
* some fields have a default value - check the code for TODO

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-nanoc-yaml-exporter``.

3. Activate the virtual environment you use for pretalx development.

4. Execute ``pip install -e .`` within this directory to register this application with pretalx's plugin registry.

5. Restart your local pretalx server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------

Copyright 2023 Johan Van de Wauw

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
.. _fosdem website: 
