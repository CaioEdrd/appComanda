from flask import Blueprint,render_template,request, redirect, url_for, abort, flash
from werkzeug.security import (generate_password_hash)
from app.extensions import (db)
from app.models.user import User
from app.forms.user_form import UserForm

cadastro_bp = Blueprint("cadastro", __name__) #bp do cadastro

@cadastro_bp.route(
    "/",
    methods=["GET", "POST"]
)
def cadastro():
    form = UserForm()
    if form.validate_on_submit():
        if form.senha.data == form.confirma_senha.data:
            if User.query.filter_by(email=form.email.data).first(): 
                flash("E-mail já cadastrado", "danger") 
                return redirect(url_for("cadastro.cadastro")) 
            else:
                usuario = User(

                    nome=form.nome.data,
                    email=form.email.data,
                    senha=generate_password_hash(form.senha.data),
                    perfil=form.perfil.data
                )

                db.session.add(usuario)

                db.session.commit()
                flash("Usuário cadastrado com sucesso!", "success")

                return redirect(
                    url_for("login.login")
                )
        else:
            flash("Senhas não correspondem!", "danger")
            return redirect(url_for("cadastro.cadastro")) 


    return render_template(
        "pages/cadastro.html", form=form
    )
