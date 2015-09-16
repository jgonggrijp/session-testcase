# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime
from random import SystemRandom
import os
import os.path as op

from .common_fixtures import BaseFixture
from ..database.models import *
from reduced_testcase.server.security import generate_key


class TipsViewTestCase(BaseFixture):
    def setUp(self):
        super(TipsViewTestCase, self).setUp()
        age = datetime(1968, 4, 4, 6, 1)
        with self.request_context():
            db.session.add(Tip(title='some book', what='book', create=age, update=age))
            db.session.add(Tip(title='some website', create=age, update=age))
            db.session.commit()

    def test_bump(self):
        with self.client as c:
            token = generate_key(SystemRandom())
            with c.session_transaction() as s:
                s['token'] = token
            c.post('/admin/tip/action/',
                   data={'action': 'Bump', 'rowid': '1', 't': token})

            with c.session_transaction(method="POST", data={'t': token}) as s:
                self.assertIn(' tips have been bumped.', s['_flashes'][0][1])
