# -*- coding: utf-8 -*-
"""
    ************
    routes.py
    ************

    
"""
__author__ = 'Jonas Van Der Donckt'

import uuid
from functools import wraps

from flask import Flask, render_template, request, jsonify, flash, session, redirect, url_for

from API.io_handler import SessionIOHandler
from API.img_db_wrappers import PISCES_RADBOUD_BD, DEMO_DB
from config import AppConfig as Ac
from forms import IntroForm

# create an instance of the application and configure it
app = Flask(__name__, template_folder=Ac.TEMPLATE_FOLDER.value, static_folder=Ac.STATIC_FOLDER.value)
app.secret_key = Ac.SECRET_KEY.value  # TODO, use a better secret key here


@app.route('/')
@app.route('/home')
@app.route('/index')
def home():
    return render_template('welkom.html')


@app.route('/intro', methods=['GET', 'POST'])
def intro():
    form = IntroForm(request.form)
    if request.method == 'POST':
        if form.validate():
            app.logger.info('request method is post')
            session['uuid'] = SessionIOHandler.create_ts_uuid(uuid=str(uuid.uuid4()))
            session['accepted_tos'] = True
            SessionIOHandler.save_metadata(
                uuid=session['uuid'],
                metadata={
                    "age": request.form['age'],
                    "sex": request.form['sex'],
                    "education": request.form['education'],
                    "device": request.form['device'],
                    "prolific_token": request.form['prolific_token']
                })
            session['prolific_token'] = request.form['prolific_token']
            return render_template("voorbeeld.html", timeout=Ac.INITIAL_TIMEOUT.value)
            # return redirect(url_for("opname"))
        else:
            # flash is not shown -> fix this ...
            flash(message=form.errors, category='danger')
            app.logger.info(form.errors)
    return render_template('intro.html', form=form)


def has_completed_intro(f):
    # validates whether participant accepted the terms of service
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'uuid' in session:  # and 'accepted_tos' in session
            return f(*args, **kwargs)
        else:
            # todo  -> make flash work
            flash('Unauthorized, Please login', category='danger')
            return redirect(url_for('intro'))

    return wrap


# ------------------------------------------------- DEBUGGING CALLS ---------------------------------------------------
@app.route('/bedankt', methods=['GET'])
def bedankt():
    prolific_code = None
    print(session)
    if 'prolific_token' in session and session['prolific_token'].lower() != 'n.a.':
        prolific_code = 'C20A4737'
    return render_template('bedankt.html', prolific_code=prolific_code)


@app.route('/video', methods=['GET'])
def video():
    return render_template('video.html')


@app.route('/opname', methods=['GET', 'POST'])
@has_completed_intro
def opname():
    # if session_index
    if 'img_index' not in session:
        assert request.method == 'GET'  # maybe remove this as it might break stuff
        # TODO -> maybe cleaner to code this in a config file ...

        #  insert the demo images in the front if applicable
        demo_images = []
        if Ac.USE_DEMO.value:
            demo_images = [(img_name, DEMO_DB.db_name) for img_name in DEMO_DB.get_shuffled_images()]

        # set the default values
        session['image_order'] = demo_images + PISCES_RADBOUD_BD.get_shuffled_images()  # names of the shuffled images
        session['image_order'] = session['image_order']
        session['img_index'] = 0  # pointer to the current image in imager order list
        session['states'] = ['marloes']  # array which is used as state machine
        session['allow_next'] = True

        # first step: let participant speak in marloes
        return render_template('marloes.html', debug=Ac.FLASK_DEBUG.value)

    # todo -> hoe iets verhogen door niet reload maar door op knop te klikken
    elif request.method == 'POST':
        if session['img_index'] != 0 and (session['img_index'] + 1) % Ac.MARLOES_MODULO.value == 0 and \
                session['states'][-1] not in ['marloes']:
            session['states'] = session['states'] + ['marloes']
            return render_template("marloes.html", debug=Ac.FLASK_DEBUG.value)

        if session['img_index'] != 0 and (session['img_index'] + 1) % Ac.PAUSE_MODULO.value == 0 \
                and session['states'][-1] not in ['pause']:
            session['states'] = session['states'] + ['pause']
            return render_template("pauze.html")

        if session['allow_next']:
            print('-' * 10, 'allow next granted', '-' * 10)
            prev_img_index = session['img_index']
            session['img_index'] = session['img_index'] + (1 if 'image' in session['states'] else 0)
            if session['img_index'] >= len(session['image_order']):
                return render_template('bedankt.html')

            print(f'\tprev_index: {prev_img_index} -> {session["image_order"][prev_img_index]}'
                  f'\tcurr_index: {session["img_index"]} -> {session["image_order"][session["img_index"]]}')

            session['states'] = session['states'] + ['image']
            session['allow_next'] = False
        else:
            print('-' * 10, 'NO ALLOW NEXT GRANTED', '-' * 10)

        img_name, db_name = session['image_order'][session['img_index']]
        if db_name.lower() == 'demo':
            static_path = DEMO_DB.get_img_path(img_name).split('static/')[1]
        else:
            static_path = PISCES_RADBOUD_BD.get_img_path(img_name=img_name, db_name=db_name).split('static/')[1]
        return render_template('afbeelding.html', index=session['img_index'], photo_path=static_path,
                               debug=Ac.FLASK_DEBUG.value, demo=db_name.lower() == 'demo')
    else:
        prev_state = session['states'][-1]
        print('[E] prev state:', prev_state, "method", request.method)
        print('[E] prev state:', prev_state, "method", request.method)

        if prev_state == 'image':
            session['states'] = session['states'] + ['image']
            img_name, db_name = session['image_order'][session['img_index']]
            if db_name.lower() == 'demo':
                static_path = DEMO_DB.get_img_path(img_name).split('static/')[1]
            else:
                static_path = PISCES_RADBOUD_BD.get_img_path(img_name=img_name, db_name=db_name).split('static/')[1]
            return render_template('afbeelding.html', index=session['img_index'], photo_path=static_path,
                                   debug=Ac.FLASK_DEBUG.value, demo=db_name.lower() == 'demo')
        elif prev_state == 'marloes':
            session['states'] = session['states'] + ['marloes']
            return render_template("marloes.html", debug=Ac.FLASK_DEBUG.value)
        return jsonify({"error": "post method but index not in session ..."})


# -------------------------------------------------- API CALLS ---------------------------------------------------
@app.route('/audio/<string:ftype>/<path:file_path>', methods=['POST'])
@has_completed_intro
def post_audio(ftype, file_path):
    if ftype.lower() == 'wav':
        session['allow_next'] = True
        SessionIOHandler.save_wav(uuid=session['uuid'], file_path=file_path, data=request.data)
        return jsonify({"status": "success"})
    elif ftype.lower() == 'blob':
        session['allow_next'] = True
        SessionIOHandler.save_wav_blob(uuid=session['uuid'], file_path=file_path, data=request.data)
        return jsonify({"status": "success"})
    elif ftype.lower() == 'ogg':
        # todo -> look into this data format
        pass
    else:
        return jsonify({"error": "invalid dtype"})


@app.route('/mood/<path:file_path>', methods=['POST'])
@has_completed_intro
def post_mood_state(file_path):
    mood_json = request.get_json()
    session['allow_next'] = True
    print(f'{file_path} obtained mood json', mood_json)
    SessionIOHandler.save_mood_json(uuid=session['uuid'], file_path=file_path, mood=mood_json)
    return jsonify({"status": "success"})


# -------------------------------------------------- ERROR HANDLING ---------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    # return a JSON when the root path is the API , ...
    root_path = str(request.path).split(sep='/')[1].upper()
    if root_path.upper() in ['API', 'LOG', 'AUDIO', 'MOOD']:
        return jsonify({"error": f"the following path is invalid: {request.path}"})
    return render_template('404.html', error=e), 404
