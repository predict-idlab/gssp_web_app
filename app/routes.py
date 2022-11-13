# -*- coding: utf-8 -*-

__author__ = "Jonas Van Der Donckt"

import uuid
from functools import wraps

from flask import Flask, render_template, request, jsonify, session

from API.io_handler import SessionIOHandler
from API.img_db_wrappers import PISCES_RADBOUD_BD, DEMO_DB
from config import AppConfig as Ac

# create an instance of the application and configure it
app = Flask(
    __name__,
    template_folder=Ac.TEMPLATE_FOLDER.value,
    static_folder=Ac.STATIC_FOLDER.value,
)
app.secret_key = Ac.SECRET_KEY.value  # TODO, use a better secret key here

# --------------- NEW ROUTES ----------------
@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    # a bare welcome page with no additional information
    return render_template("welcome.html")


@app.route("/home/<user_id>")
def experiment(user_id):
    headers = dict(request.headers)
    uuid_str = "_".join(["ACE", user_id, str(uuid.uuid4())])
    session["uuid"] = uuid_str
    session["user_id"] = user_id

    # store the user_id in the uuid folder
    SessionIOHandler.save_metadata_sf(
        uuid=uuid_str, metadata={"user_id": user_id, "headers": headers}
    )

    # Construct the image order of the to-be saved images
    img_order = [
        ("Picture 81.jpg", "PisCES"),
        ("Picture 88.jpg", "PisCES"),
    ]

    photo_paths = [
        PISCES_RADBOUD_BD.get_img_path(img_name=img_name, db_name=db_name).split(
            "static/"
        )[1]
        for img_name, db_name in img_order
    ]
    return render_template("experiment.html", user_id=user_id, photo_paths=photo_paths)


def has_set_uuid(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return page_not_found("Unauthorized, Please use a link with an UUID")
        return f(*args, **kwargs)

    return wrap


@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")


# -------------------------------- API CALLS ------------------------------------------
@app.route("/audio/<string:ftype>/<path:file_path>", methods=["POST"])
@has_set_uuid
def post_audio(ftype, file_path):
    if ftype.lower() == "wav":
        session["allow_next"] = True
        SessionIOHandler.save_wav(
            uuid=session["uuid"], file_path=file_path, data=request.data
        )
        return jsonify({"status": "success"})
    elif ftype.lower() == "blob":
        session["allow_next"] = True
        SessionIOHandler.save_wav_blob(
            uuid=session["uuid"], file_path=file_path, data=request.data
        )
        return jsonify({"status": "success"})
    elif ftype.lower() == "ogg":
        # todo -> look into this data format
        pass
    else:
        return jsonify({"error": "invalid dtype"})


# ------------------------ ERROR HANDLING -----------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    # return a JSON when the root path is the API , ...
    root_path = str(request.path).split(sep="/")[1].upper()
    if root_path.upper() in ["API", "LOG", "AUDIO"]:
        return jsonify({"error": f"the following path is invalid: {request.path}"})
    return render_template("404_en.html", error=e)
