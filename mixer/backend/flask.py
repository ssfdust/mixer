""" Module integrate the Mixer to Flask application.

See example: ::

    from mixer.backend.flask import mixer

    mixer.init_app(flask_app)

    user = mixer.blend('path.to.models.User')

"""
from __future__ import absolute_import

from typing import Any, Optional

from flask.app import Flask

from .sqlalchemy import Mixer as BaseMixer
from .sqlalchemy import TypeMixer


class Mixer(BaseMixer):

    """ Init application. """

    type_mixer_cls = TypeMixer

    def __init__(
        self, app: Optional[Any] = None, commit: bool = True, **kwargs: Any
    ) -> None:
        """Initialize the SQLAlchemy Mixer.

        :param fake: (True) Generate fake data instead of random data.
        :param app: Flask application
        :param commit: (True) Commit instance to session after creation.

        """
        super(Mixer, self).__init__(**kwargs)
        self.params["commit"] = commit
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Init application.

        This callback can be used to initialize an application for the
        use with this mixer setup.

        :param app: Flask application

        """
        assert (
            app.extensions and app.extensions["sqlalchemy"]
        ), "Flask-SQLAlchemy must be inialized before Mixer."
        db = app.extensions["sqlalchemy"].db
        self.params["session"] = db.session

        # register extension with app
        app.extensions["mixer"] = self


# Default mixer
mixer = Mixer(commit=True)

# lint_ignore=W0201
