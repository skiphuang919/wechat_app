from flask import redirect, url_for, request, session, jsonify, \
    current_app, render_template, flash
from ..lib.wc_lib import WeChat
from ..lib import user
from . import auth
from .form import UserForm
from ..lib.user import is_email_exist, is_name_exist
from ..email import send_confirm_mail


#@auth.before_app_request
def before_request():
    if request.endpoint != 'auth.wc_oauth2':
        if session.get('openid') is None:
            session['redirect_url_endpoint'] = request.endpoint
            we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
            oauth2_url = we_chat.get_oauth2_url(redirect_url=url_for('auth.wc_oauth2', _external=True))
            return redirect(oauth2_url)


@auth.route('/wc_oauth2', methods=['GET', 'POST'])
def wc_oauth2():
    code = request.args.get('code', None)
    if code is not None:
        we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
        token_info = we_chat.get_web_access_token_by_code(code)
        openid = token_info.get('openid', None)
        if openid:
            session['openid'] = openid
            url_endpoint = session.get('redirect_url_endpoint', 'index')
            return redirect(url_for(url_endpoint))
    return jsonify({'msg': 'Authorization failed, please try again.'})


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.is_submitted():
        if form.validate():
            if is_email_exist(form.email.data):
                flash('Email already exist.')
            elif is_name_exist(form.name.data):
                flash('Name already exist.')
            else:
                new_user = user.add_user(name=form.name.data,
                                         email=form.email.data,
                                         gender=form.gender.data,
                                         city=form.gender.data,
                                         slogan=form.slogan.data)
                token = new_user.generate_confirm_token()
                send_confirm_mail('Confirm Your Account', new_user.email, new_user.name, token)
                return redirect(url_for('auth.reg_success'))
        else:
            form_error = form.errors.items()[0]
            f_error = form_error[1][0]
            flash(f_error)
    return render_template('register.html', form=form)


@auth.route('/reg_success')
def reg_success():
    return render_template('success.html', success_title='Register Successfully',
                           success_detail='A confirmation email has been sent to you by email.')


@auth.route('/confirm')
def confirm():
    pass
