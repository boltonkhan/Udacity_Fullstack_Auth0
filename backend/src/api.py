"""An API for a Udacity Coffee Shop."""

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)


def check_drink_body(body):
    """Check if the drink body is in a complemetary format."""
    if not body:
        return False

    title = body.get("title", None)
    recipe = body.get("recipe", None)

    if not isinstance(recipe, list):
        return False

    for r in recipe:
        color = r.get("color", None)
        name = r.get("name", None)
        parts = r.get("parts", None)

        if not color or not name or not parts:
            return False

        try:
            int(parts)

        except ValueError:
            return False

    return True


@app.before_request
def before_request():
    """Add headers to each request."""
    headers = dict(request.headers)
    headers["Access-Control-Allow-Origin"] = "*"
    headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PATCH"
    headers["Content-Type"] = "application/json"
    request.headers = headers


@app.route('/')
def dummy():
    """Return dummy text just for a run."""
    return jsonify({'Dummy done just for run.': 'done'}), 200


db_drop_and_create_all()


@app.route("/drinks", methods=["GET"])
def get_drinks():
    """Get all drinks existing in the database."""
    drinks = None
    try:
        drinks = Drink.query.all()

    except Exception as e:
        print(e)
        abort(500)

    if drinks is None:
        abort(404)

    drinks = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_details(payload):
    """Get all drinks existing in the database a with detailed info."""
    drinks = None
    try:
        drinks = Drink.query.all()

    except Exception as e:
        print(e)
        abort(500)

    if drinks is None:
        abort(404)

    drinks = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink(payload):
    """Get all drinks existing in the database a with detailed info."""
    body = request.get_json()
    if not check_drink_body(body):
        abort(400)

    title = json.dumps(body.get("title"))
    recipe = json.dumps(body.get("recipe"))

    try:
        drink = Drink(title=title, recipe=recipe)
        drink = drink.insert()

    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    """Update given drink data.

    :param id: drink id
    :id type: int
    :param payload: decoded auth0 token
    :payload type: str
    """
    drink = None

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

    except Exception as e:
        print(e)
        abort(500)

    if not drink:
        abort(404)

    body = request.get_json()

    if not body:
        abort(400)

    title = body.get("title", None)
    if title:
        drink.title = title

    recipe = recipe = body.get("recipe", None)
    if recipe:

        if not isinstance(recipe, list):
            abort(400)

        for i in enumerate(recipe):

            color = recipe[i].get("color", None)
            if color:
                drink.recipe[i].color = color

            name = recipe[i].get("name", None)
            if name:
                drink.recipe[i].name = name

            parts = recipe[i].get("parts", None)
            if parts:
                drink.recipe[i].parts = parts

    try:
        drink = drink.update()

    except Exception as e:
        print(e)
        abort(500)

    return jsonify({
        "success": True,
        "drinks": [
            drink.long()
        ]
    })


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    """Delete the drink.

    :param id: drink id
    :id type: int
    :param payload: decoded auth0 token
    :payload type: str
    """
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

    except Exception as e:
        print(e)
        abort(500)

    if not drink:
        abort(404)

    try:
        drink.delete()

    except Exception as e:
        print(e)
        abort(500)

    return jsonify({
        "success": True,
        "delete": id
    })


@app.errorhandler(422)
def unprocessable(error):
    """Handle unprocessable entity error."""
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    """Handle resource not found entity error."""
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    """Handle authorisation error."""
    message = error.error["description"]
    status = error.status_code
    return jsonify({
        "success": False,
        "error": status,
        "message": message
    }), status


@app.errorhandler(500)
def server_error(error):
    """Handle general server error."""
    print(error)
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Something went wrong."
    })


if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")
