# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime, timedelta

from flask import json, session

from ..common_fixtures import BaseFixture
from ...database.models import *
from ...database.db import db


class ReflectionTestCase (BaseFixture):
    def setUp(self):
        super(ReflectionTestCase, self).setUp()
        now = datetime.today()
        reflection3 = BrainTeaser(title='reflection3', publication=now - timedelta(weeks=1))
        ses = db.session
        with self.request_context():
            ses.add(reflection3)
            ses.commit()
    
    def test_reply_to_reflection_passthrough(self):
        with self.client as c:
            token = 'abcdef'

            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(hours=1)
            
            response2 = c.post('/reflection/1/reply', data={
                'p': 'test4',
                'r': 'testmessage',
                't': token,
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
            })
            self.assertEqual(response2.status_code, 200)
            self.assertIn('json', response2.mimetype)
            response_data = json.loads(response2.data)
            self.assertEqual(response_data['status'], 'success')
            self.assertEqual(response_data['token'], session['token'])
            
            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(milliseconds=1001)
            
            response3 = c.post('/reflection/1/reply', data={
                'p': 'test4',
                'r': 'testmessage',
                't': token,
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
            })
            self.assertEqual(response3.status_code, 200)
            self.assertIn('json', response3.mimetype)
            response_data = json.loads(response3.data)
            self.assertEqual(response_data['token'], session['token'])
            self.assertEqual(response_data['status'], 'captcha')
            
