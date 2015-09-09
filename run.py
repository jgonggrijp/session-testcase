#!/usr/bin/env python

# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Run a local test server with the serverside application.
"""

from reduced_testcase import create_app


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testcase.db'
    SECRET_KEY = '123456'
    CAPTCHA_DATA = 'reduced_testcase/tests/test_captcha.json'

if __name__ == '__main__':
    app = create_app(config_obj=Config)
    app.debug = True
    app.run(port=5004)
