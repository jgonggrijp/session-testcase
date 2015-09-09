# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Authors: Julian Gonggrijp, j.gonggrijp@uu.nl,
#          Martijn van der Klis, m.h.vanderklis@uu.nl

"""
    Directly visitable routes on the domain.
"""

from datetime import date, datetime, timedelta

from flask import send_from_directory, jsonify, current_app, abort, request, escape, session, make_response

from ..database.models import *
from ..database.db import db
from .blueprint import public
from .security import session_enable, session_protect, init_captcha, captcha_safe


ISOFORMAT = '%Y-%m-%d %H:%M:%S.%f'
POST_INTERVAL = timedelta(minutes=10)


@public.route('/')
def index():
    return send_from_directory(public.static_folder, 'index.html')


@public.route('/reflection/')
@session_enable
def current_reflection():
    latest_reflection = available_reflection().first()
    if not latest_reflection or not latest_reflection.publication:
        abort(404)
    return reflection2dict(latest_reflection, True)


@public.route('/reflection/<int:id>/')
def retrieve_reflection(id):
    reflection = BrainTeaser.query.get_or_404(id)
    if not reflection.publication or reflection.publication > date.today():
        abort(404)
    return jsonify(**reflection2dict(reflection, True))


def reflection2dict(reflection, with_responses=False):
    if reflection.closure:
        closure = str(reflection.closure)
    else:
        closure = None
    if with_responses:
        replies = reflection_replies(reflection.id)
    else:
        replies = None
    now = datetime.today()
    return {
        'id': reflection.id,
        'title': reflection.title,
        'publication': str(reflection.publication),
        'week': reflection.publication.isocalendar()[1],
        'closure': closure,
        'text': reflection.text,
        'responses': replies,
        'since': str(now),
    }


def available_reflection():
    now = date.today()
    return (
        BrainTeaser.query
        .filter(BrainTeaser.publication != None)
        .filter(BrainTeaser.publication <= now)
        .order_by(BrainTeaser.publication.desc())
    )


def response2dict(response):
    return {
        'submission': str(response.submission.date()),
        'pseudonym': response.pseudonym,
        'message': response.message,
        'id': response.id,
        'up': response.upvotes,
        'down': response.downvotes,
    }


def reflection_replies(id, since=None):
    query = Response.query.filter_by(brain_teaser_id=id)
    if since is not None:
        if isinstance(since, str) or isinstance(since, unicode):
            since = datetime.strptime(since, ISOFORMAT)
        query = query.filter(Response.submission >= since)
    return map(response2dict, query.order_by(Response.submission).all())


@public.route('/reflection/archive')
def reflection_archive():
    return jsonify(all=map(reflection2dict, available_reflection()))


@public.route('/reflection/<int:id>/reply', methods=['POST'])
@session_protect
def reply_to_reflection(id):
    now = datetime.today()
    topic = BrainTeaser.query.get_or_404(id)
    if topic.closure and topic.closure <= now.date():
        return {'status': 'closed'}, 400
    if 'last-retrieve' in request.form:
        ninjas = reflection_replies(id, request.form['last-retrieve'])
        if ninjas:
            return {
                'status': 'ninja',
                'new': ninjas,
                'since': str(now),
            }
    if ( 'p' not in request.form or not request.form['p']
         or 'r' not in request.form or not request.form['r'] ):
        return {'status': 'invalid'}, 400
    if ( 'last-reply' in session and
         now - session['last-reply'] < POST_INTERVAL and
         not 'captcha-answer' in session ):
        return dict(status='captcha', **init_captcha())
    # code below does not enforce quarantine period.
    # in order to make it happen, return {status: quarantine} if not 
    # captcha_safe.
    if (not captcha_safe() or 'captcha-quarantine' in session):
        return dict(status='captcha', **init_captcha())
    db.session.add(Response(
        brain_teaser=topic,
        submission=now,
        pseudonym=escape(request.form['p'].strip())[:30],
        message=escape(request.form['r'].strip())[:400]
    ))
    db.session.commit()
    session['last-reply'] = now
    return {'status': 'success'}


@public.route('/reply/<int:id>/moderate/', methods=['POST'])
@session_protect
def moderate_reply(id):
    if 'choice' not in request.form:
        return {'status': 'invalid'}, 400
    choice = request.form['choice']
    try:
        target = Response.query.filter_by(id=id).one()
    except:
        return {'status': 'unavailable'}, 400
    ses = db.session
    if choice == 'up':
        target.upvotes += 1
        ses.commit()
        return {'status': 'success'}
    elif choice == 'down':
        target.downvotes += 1
        ses.commit()
        return {'status': 'success'}
    else:
        return {'status': 'invalid'}, 400

