from functools import wraps
from flask import Blueprint,render_template,request, redirect, url_for, abort, flash
from flask_login import (login_user,logout_user,current_user,login_required)
from werkzeug.security import (check_password_hash)
from app.extensions import (db,login_manager)
from app.models.user import User
from app.forms.user_form import LoginForm

login_bp = Blueprint("login", __name__) #bp do login


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )


@login_bp.route(
    "/",
    methods=["GET", "POST"]
)
def login():
    form = LoginForm()

    if form.validate_on_submit():

        usuario = User.query.filter_by(
            email=form.email.data
        ).first()

        if (usuario and check_password_hash(usuario.senha,form.senha.data)):

            login_user(usuario)
            flash("Login realizado com sucesso!", "success")

            return redirect(
                url_for("home.home")
            )
        else:
            flash("E-mail ou senha incorreto!", "Danger")


    return render_template( "pages/login.html", form=form)

@login_bp.route("/logout")
@login_required
def logout():

    logout_user()
    flash("Logout realizado com sucesso!", "success")

    return redirect(
        url_for("login.login")
    )
