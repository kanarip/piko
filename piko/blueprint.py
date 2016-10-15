from flask import Blueprint as FlaskBlueprint

class Blueprint(FlaskBlueprint):
    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.logger = app.logger
        super(Blueprint, self).__init__(*args, **kwargs)

    def abort(self, *args, **kwargs):
        return self.app.abort(*args, **kwargs)

    def render_template(self, *args, **kwargs):
        return self.app.render_template(*args, **kwargs)

