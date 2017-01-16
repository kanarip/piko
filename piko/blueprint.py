"""
    A :py:class:`piko.blueprint.Blueprint` is a proxy to a
    :py:class:`flask.Blueprint`.
"""
from flask import Blueprint as FlaskBlueprint


class Blueprint(FlaskBlueprint):
    """
        A :py:class:`flask.Blueprint`
    """

    def __init__(self, app, *args, **kwargs):
        """
            Invoke the parent with our proxied objects.
        """
        self.app = app
        self.logger = app.logger
        super(Blueprint, self).__init__(*args, **kwargs)

    def abort(self, *args, **kwargs):
        """
            Proxy the .abort() function.
        """
        return self.app.abort(*args, **kwargs)

    def render_template(self, *args, **kwargs):
        """
            Proxy the .render_template() function.
        """
        return self.app.render_template(*args, **kwargs)
