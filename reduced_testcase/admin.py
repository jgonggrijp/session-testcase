# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Admin factory for use with the main Flask application.
"""

from datetime import datetime

from wtforms import validators, widgets
from flask import current_app, flash
from flask.ext.admin import form, Admin
from flask.ext.admin.actions import action, ActionsMixin
from flask.ext.admin.contrib.sqla import ModelView

from .database import db
from .database.models import *


__all__ = ['create_admin']


class BrainTeasersView(ModelView):
    column_list = ('title', 'publication', 'closure')
    form_columns = ('title', 'publication', 'closure', 'text')

    def __init__(self, session, name='Brain teasers', **kwargs):
        super(BrainTeasersView, self).__init__(BrainTeaser, session, name, **kwargs)


class TipsView(ModelView):
    column_list = ('what', 'author', 'title', 'update')
    form_columns = ('what', 'author', 'title', 'text', 'href')
    form_args = {
        'text': {
            'label': 'Description',
        },
        'href': {
            'label': 'Hyperlink',
            'validators': [validators.URL(),],
            'widget': widgets.TextInput(),
        },
    }

    def on_model_change(self, form, model, is_created=True):
        model.update = datetime.now()
        if is_created:
            model.create = model.update

    @action('Bump', 'Mark as updated')
    def bump(self, ids):
        now = datetime.now()
        count = Tip.query.filter(Tip.id.in_(ids)).update({Tip.update: now}, False)
        db.session.commit()
        flash('{} tips have been bumped.'.format(count))

    def __init__(self, session, name='Tips', **kwargs):
        super(TipsView, self).__init__(Tip, session, name, **kwargs)


def create_admin(app):
    """ Create an Admin object on Flask instance `app` and return it.
    """
    admin = Admin(name='Reduced test')
    ses = db.session
    admin.add_view(BrainTeasersView(ses))
    admin.add_view(TipsView(ses))
    admin.init_app(app)
    return admin
