# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime, timedelta

from flask import json, session

from ..common_fixtures import BaseFixture
from ...server.security import *


class AuthorizeCaptchaTestCase (BaseFixture):
    def setUp(self):
        super(AuthorizeCaptchaTestCase, self).setUp()
        @self.app.route('/test', methods=['POST'])
        def testview():
            return '', 200 if authorize_captcha() else 400
    
    def test_authorize_captcha_expired(self):
        with self.client as c:
            token = generate_key(SystemRandom())
            with c.session_transaction() as s:
                s['token'] = token
                s['captcha-answer'] = u'one two three'.split()
                s['captcha-expires'] = datetime.today() - timedelta(minutes=1)
            self.assertEqual(c.post('/test', data={
                'ca': 'one two three',
                't': token
            }).status_code, 400)
    
    def test_authorize_captcha_validation(self):
        with self.client as c:
            token = generate_key(SystemRandom())
            with c.session_transaction() as s:
                s['token'] = token
                s['captcha-expires'] = datetime.today() + timedelta(minutes=10)
                s['captcha-answer'] = u'one two three'.split()
            self.assertEqual(c.post('/test', data={
                'ca': 'one two three',
                't': token
            }).status_code, 200)
            self.assertEqual(c.post('/test', data={
                'ca': 'one two four',
                't': token
            }).status_code, 400)


class CaptchaSafeTestCase (BaseFixture):
    def setUp(self):
        super(CaptchaSafeTestCase, self).setUp()
        @self.app.route('/test', methods=['POST'])
        def testview():
            return '', 200 if captcha_safe() else 400
    
    def test_captcha_safe_unauthorized(self):
        with self.client as c:
            token = generate_key(SystemRandom())
            with c.session_transaction() as s:
                s['token'] = token
                s['captcha-expires'] = datetime.today() + timedelta(minutes=10)
                s['captcha-answer'] = u'one two three'.split()
            now = datetime.today()
            self.assertEqual(c.post('/test', data={
                't': token
            }).status_code, 400)
            self.assertEqual(len(session), 3)
            self.assertIn('captcha-quarantine', session)
            self.assertTrue(session.permanent)
    
    def test_captcha_safe_inquarantine(self):
        with self.client as c:
            quarantine = datetime.today().replace(microsecond=0) + QUARANTINE_TIME
            with c.session_transaction() as s:
                s['captcha-quarantine'] = quarantine
            self.assertEqual(c.post('/test').status_code, 400)
            self.assertIn('captcha-quarantine', session)
            self.assertEqual(session['captcha-quarantine'], quarantine)
    

class VerifyNaturalTestCase (BaseFixture):
    def setUp(self):
        super(VerifyNaturalTestCase, self).setUp()
        @self.app.route('/test', methods=['POST'])
        def testview():
            verify_natural()
            return '', 200
    
    def test_verify_natural(self):
        with self.client as c:
            for flags in range(8):  # lo2hi: user agent, referer, tainted
                headerfields = {}
                with c.session_transaction() as s:
                    s.clear()
                if flags & 1:
                    headerfields['User-Agent'] = 'Flask test client'
                if flags & 2:
                    headerfields['Referer'] = 'unittest'
                if flags & 4:
                    with c.session_transaction() as s:
                        s['tainted'] = True
                status = c.post('/test', headers=headerfields).status_code
                tainted = 'tainted' in session
                if flags == 3:
                    self.assertFalse(tainted)
                    self.assertEqual(status, 200)
                else:
                    self.assertTrue(tainted)
                    self.assertEqual(status, 400)
    
