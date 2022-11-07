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
def home(user_id):
    headers = dict(request.headers)
    uuid_str = "_".join(["ACE", user_id, str(uuid.uuid4())])
    session["uuid"] = uuid_str
    session["user_id"] = user_id

    # quick fix to allow multiple runs in same browser
    # i.e., the /home/user_id route resets everything
    session.pop("img_index", None)
    session.pop("img_order", None)

    # store the user_id in the uuid folder
    SessionIOHandler.save_metadata_sf(
        uuid=uuid_str, metadata={"user_id": user_id, "headers": headers}
    )
    return render_template("welcome_info.html", user_id=user_id)


def has_set_uuid(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return page_not_found("Unauthorized, Please use a link with an UUID")
        return f(*args, **kwargs)

    return wrap


@app.route("/recording", methods=["GET", "POST"])
@has_set_uuid
def recording():
    if "img_index" not in session:
        # Base case: first time the recording page is loaded
        session["img_order"] = [
            ("Picture 81.jpg", "PisCES"),
            ("Picture 88.jpg", "PisCES"),
        ]
        session["img_index"] = 0  # pointer to the current image

        # Flag to allow a user to go to the next image
        # NOTE: allow_next will be set to True when the audio was uploaded sucessfully
        session["allow_next"] = False

        # Get the first image it's path and render the template
        img_name, db_name = session["img_order"][session["img_index"]]
        static_path = PISCES_RADBOUD_BD.get_img_path(
            img_name=img_name, db_name=db_name
        ).split("static/")[1]
        return render_template(
            "image.html",
            index=session["img_index"],
            photo_path=static_path,
            debug=Ac.FLASK_DEBUG.value,
            demo=db_name.lower() == "demo",
            continue_text="Continue",
        )
    else:
        if session["allow_next"]:  # increase the image index
            print("-" * 10, "allow next granted", "-" * 10)
            session["img_index"] = session["img_index"] + 1

            # edge case: last image
            if session["img_index"] >= len(session["img_order"]):
                return render_template("thank_you.html")

            session["allow_next"] = False
        else:
            print("-" * 10, "NO ALLOW NEXT GRANTED", "-" * 10)

        # load the next image and render the template
        img_name, db_name = session["img_order"][session["img_index"]]
        static_path = PISCES_RADBOUD_BD.get_img_path(
            img_name=img_name, db_name=db_name
        ).split("static/")[1]
        continue_text = (
            "Continue"
            if session["img_index"] < len(session["img_order"]) - 1
            else "Finish"
        )

        return render_template(
            "image.html",
            index=session["img_index"],
            photo_path=static_path,
            debug=Ac.FLASK_DEBUG.value,
            demo=db_name.lower() == "demo",
            continue_text=continue_text,
        )


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
