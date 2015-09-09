# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime
import os
import os.path as op

from .common_fixtures import BaseFixture
from ..database.models import *


class TipsViewTestCase(BaseFixture):
    def setUp(self):
        super(TipsViewTestCase, self).setUp()
        age = datetime(1968, 4, 4, 6, 1)
        with self.request_context():
            db.session.add(Tip(title='some book', what='book', create=age, update=age))
            db.session.add(Tip(title='some website', create=age, update=age))
            db.session.commit()

    def test_bump(self):
        response = self.client.post(
            '/admin/tip/action/',
            data = {'action': 'Bump', 'rowid': '1',},
            follow_redirects=True )
        self.assertIn(' tips have been bumped.', response.data)
