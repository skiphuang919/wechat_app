from flask import redirect, url_for, request, session, jsonify, \
    current_app, render_template, flash
from ..lib.wc_lib import WeChat
from . import auth
from .form import UserForm
from ..lib import users
from ..email import send_confirm_mail
from flask_login import login_user, current_user, login_required

CONFIRM_MAIL_SUBJECT = '[Zombie Zone] Confirm Your Email From'


@auth.before_app_request
def before_request():
    """
    login the user by open id if it exist
    otherwise redirect to wechat oauth url
    """
    if request.endpoint not in ['auth.wc_oauth2', 'auth.confirm', 'static']:
        if session.get('openid') is None:
            session['redirect_url_endpoint'] = request.endpoint
            we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
            oauth2_url = we_chat.get_oauth2_url(redirect_url=url_for('auth.wc_oauth2', _external=True))
            return redirect(oauth2_url)
        else:
            user = users.get_user(open_id=session.get('openid'))
            if user:
                login_user(user, remember=True)


@auth.route('/wc_oauth2', methods=['GET', 'POST'])
def wc_oauth2():
    """
    to be call back by wechat oauth with code
    then get open id by the code
    """
    code = request.args.get('code', None)
    if code is not None:
        we_chat = WeChat(current_app.config.get('APP_ID'), current_app.config.get('APP_SECRET'))
        token_info = we_chat.get_web_access_token_by_code(code)
        openid = token_info.get('openid', None)
        if openid:
            session['openid'] = openid
            user = users.get_user(open_id=session.get('openid'))
            if user:
                login_user(user, remember=True)
            url_endpoint = session.get('redirect_url_endpoint', 'index')
            return redirect(url_for(url_endpoint))
    return jsonify({'msg': 'Authorization failed, please try again.'})


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.is_submitted():
        if not current_user.is_anonymous:
            warn_msg = 'You have registered before.'
        else:
            if form.validate():
                if users.is_email_exist(form.email.data):
                    warn_msg = 'Email already exist.'
                elif users.is_name_exist(form.name.data):
                    warn_msg = 'Name already exist.'
                else:
                    open_id = session.get('openid')
                    new_user = users.add_user(open_id=open_id,
                                              name=form.name.data,
                                              email=form.email.data,
                                              gender=form.gender.data,
                                              city=form.gender.data,
                                              slogan=form.slogan.data)
                    token = new_user.generate_confirm_token()
                    send_confirm_mail(CONFIRM_MAIL_SUBJECT, new_user.email, new_user.name, token)
                    print token
                    flash('A confirmation email has been sent to your mailbox.', category='message')
                    return redirect(url_for('main.index'))
            else:
                form_error = form.errors.items()[0]
                warn_msg = form_error[1][0]
        flash(warn_msg, category='warn')
    return render_template('register.html', form=form)


@auth.route('/confirm/<token>')
def confirm(token):
    if users.confirm(token):
        return render_template('success.html',
                               success_title='Success',
                               success_detail='Your email address has been confirmed successfully.')
    else:
        return render_template('warn.html',
                               warn_title='Failed',
                               warn_detail='The confirmation link is invalid or has expired.')


@auth.route('/resend_confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirm_token()
    send_confirm_mail(CONFIRM_MAIL_SUBJECT, current_user.email, current_user.name, token)
    flash('A new confirmation email has been sent to you by email.', category='message')
    return redirect(url_for('main.index'))
