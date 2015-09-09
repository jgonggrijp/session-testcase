# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Object relational model and database schema.
    
    An organogram will be provided as external documentation of the
    database structure.
"""

import os

from flask import current_app

from db import db


class Session(db.Model):
    """ Server-side storage medium for the sessions. """
    token   = db.Column(db.String(30), primary_key=True)
                                # 30 = ..server.security.KEY_LENGTH
                                # (not imported here because of circularity)
    expires = db.Column(db.DateTime)
    payload = db.Column(db.PickleType)


class BrainTeaser (db.Model):
    """ Periodic reflection item that users may discuss publicly.
    """
    id          = db.Column(db.Integer, primary_key=True)
    publication = db.Column(db.Date)
    closure     = db.Column(db.Date)
    title       = db.Column(db.Text)
    text        = db.Column(db.Text)
    
    def __str__(self):
        return self.title


class Response (db.Model):
    """ Response to the discussion associated with a brain teaser.
    """
    id              = db.Column(db.Integer, primary_key=True)
    brain_teaser_id = db.Column(db.ForeignKey('brain_teaser.id'), nullable=False)
    submission      = db.Column(db.DateTime, nullable=False)
    pseudonym       = db.Column(db.String(30), nullable=False)
    upvotes         = db.Column(db.Integer, default=0)
    downvotes       = db.Column(db.Integer, default=0)
    message         = db.Column(db.Text, nullable=False)
    brain_teaser    = db.relationship('BrainTeaser', backref='responses')


class Tip (db.Model):
    """ Any reference that the content provider opts to share with users.
    """
    id      = db.Column(db.Integer, primary_key=True)
    create  = db.Column(db.DateTime, nullable=False)
    update  = db.Column(db.DateTime, nullable=False)
    what    = db.Column(db.Enum('book', 'site', name='what_types'))
    author  = db.Column(db.Text)
    title   = db.Column(db.Text, nullable=False)
    text    = db.Column(db.Text)
    href    = db.Column(db.Text)
