# Pretalx exporter for nanoc (FOSDEM)

This is a plugin for [pretalx](https://github.com/pretalx/pretalx) that
builds a yaml file that can be consumed by the [fosdem
website](https://github.com/FOSDEM/website) nanoc build.

Note this is a first version/proof of concept. Bug reports and pull
requests are highly appreciated.

Features not yet implemented are:
* ordering of tracks (may need a change/plugin in pretalx?)
* track type (eg main track/keynote)
* some fields have a default value - check the code for TODO
* logo for talks/images for speaker - check need for resizing

## Development setup

1.  Make sure that you have a working [pretalx development
    setup](https://docs.pretalx.org/en/latest/developer/setup.html).
2.  Clone this repository, eg to `local/pretalx-nanoc-yaml-exporter`.
3.  Activate the virtual environment you use for pretalx development.
4.  Execute `pip install -e .` within this directory to register this
    application with pretalx\'s plugin registry.
5.  Restart your local pretalx server. You can now use the plugin from
    this repository for your events by enabling it in the \'plugins\'
    tab in the settings.

## Test building the website

1.  If you have a running pretalx setup, either create a conference from
    scratch or create a dummy conference by running
    
```
./manage.py create_test_event
```

2. Ensure the plugin is installed (as mentioned above) and activated for the conference
3. From a checked out version of the FOSDEM website in the [pretalx branch](https://github.com/FOSDEM/website/tree/pretalx) , run

```
curl http://localhost:8000/democon/schedule/export/NanocExporter -o export/pentabarf.yaml
nanoc
nanoc view
```
replace democon with the name of the conference.

4. To export the static files (attachments/logo/...) run
```
./manage.py export_schedule_html $confname
```

This will export a static html version of the pretalx schedule with all its media assets to the folder you configured in your pretalx.cfg file under filesystem.data. $data/htmlexport/<confname>. 

## License

Copyright 2023 Johan Van de Wauw

Released under the terms of the Apache License 2.0
