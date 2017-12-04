"""Backoffice website"""

from flask import Blueprint, request, make_response, jsonify, render_template, redirect,\
    url_for, session, flash
from app import ADMIN_USER, ADMIN_PWD

WEBSITE_BLUEPRINT = Blueprint('website', __name__, url_prefix="/website")


@WEBSITE_BLUEPRINT.route("/login", methods=["GET", "POST"])
def login():
    """Login template/login form submitter"""
    if request.method == 'POST':
        data = request.form
        user = data.get("user", "")
        pwd = data.get("password", "")
        if user == ADMIN_USER and pwd == ADMIN_PWD:
            session['admin'] = True
            return redirect(url_for("website.index"))
    return render_template("login.html")


@WEBSITE_BLUEPRINT.route("/logout")
def logout():
    """Home for backoffice website"""
    flash('You were logged out')
    session['admin'] = False
    return redirect(url_for("website.index"))


@WEBSITE_BLUEPRINT.route("")
def index():
    """Home for backoffice website"""
    if not session.get('admin', False):
        return redirect(url_for('website.login'))

    return render_template("home.html")

