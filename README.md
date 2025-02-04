# FOSDEM pretalx integration

For edition 2024 of FOSDEM, we have switched to using [pretalx](https://github.com/pretalx/) instead of pentabarf.

This repository is the home of plugins and scripts we use to customize pretalx.

It contains several plugins:
* auditlog
  * this plugin keeps a log of changes
* pretalx-suggest
  * form used to suggest new speakers for main between FOSDEM editions.
* pretalx-fringe:
  * form used for publishing fringe activities at [FOSDEM fringe](https://fosdem.org/fringe/)
* devroom-settings:
  * main module which contains customizations to link manager teams and review teams to tracks, and store other settings relevant for devrooms. Also the export used by nanoc for building the website is part of this repository.

Note that it is required to use our fork of pretalx for using the devroom-settings plugin, because there are still some custom changes in the code required to make everything run.
