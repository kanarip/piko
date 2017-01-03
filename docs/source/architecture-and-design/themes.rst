======
Themes
======

A theme is a hierarchy of templates and assets in `./piko/themes/`. Two themes
are provided, *default* and *demo*, that show how themeing can be used in
practice.

A theme basically registers additional assets, and
:py:module:`flask.ext.themes` ensures templates and the like are lookup up in
the correct location.
