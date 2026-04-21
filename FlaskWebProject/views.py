"""
Routes and views for the flask application.
"""

from flask import render_template, flash, redirect, request, session, url_for
from werkzeug.urls import url_parse
from config import Config
from FlaskWebProject import app
from FlaskWebProject.forms import LoginForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from FlaskWebProject.models import User, Post
import msal
import uuid

imageSourceUrl = 'https://'+ app.config['BLOB_ACCOUNT']  + '.blob.core.windows.net/' + app.config['BLOB_CONTAINER']  + '/'

@app.route('/')
@app.route('/home')
@login_required
def home():
    _user = User.query.filter_by(username=current_user.username).first_or_404()
    posts = Post.query.all()
    return render_template(
        'index.html',
        title='Home Page',
        posts=posts
    )

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm(request.form)
    if form.validate_on_submit():
        post = Post()
        post.save_changes(form, request.files['image_path'], current_user.id, new=True)
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Create Post',
        imageSource=imageSourceUrl,
        form=form
    )


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    post = Post.query.get(int(id))
    form = PostForm(formdata=request.form, obj=post)
    if form.validate_on_submit():
        post.save_changes(form, request.files['image_path'], current_user.id)
        return redirect(url_for('home'))
    return render_template(
        'post.html',
        title='Edit Post',
        imageSource=imageSourceUrl,
        form=form
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug(f"/login[{request.method}] - endpoint starting...")
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            app.logger.warning("/login - user failed to log in")
            flash('Invalid username or password')
            return redirect(url_for('login'))
        app.logger.info(f"/login - user {user} successfully logged in with a form-provided username/password")
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    session["state"] = str(uuid.uuid4())
    app.logger.debug("/login - starting auth url flow...")
    auth_url = _build_auth_url(authority=Config.AUTHORITY, scopes=Config.SCOPE, state=session["state"])
    return render_template('login.html', title='Sign In', form=form, auth_url=auth_url)

@app.route(Config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    app.logger.debug(f"/authorized ({Config.REDIRECT_PATH}) - endpoint starting with {request.args =} and {session =}")
    if request.args.get('state') != session.get("state"):
        app.logger.error(f"/authorized ({Config.REDIRECT_PATH}) - missing state or mismatch on state (request.args == {request.args} and session['state'] == {session.get('state')}), rerouting home.")
        return redirect(url_for("home"))  # No-OP. Goes back to Index page
    if "error" in request.args:  # Authentication/Authorization failure
        app.logger.error(f"/authorized ({Config.REDIRECT_PATH}) - error in request.args: {request.args}, User failed login attempt.")
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        app.logger.debug(f"/authorized ({Config.REDIRECT_PATH}) - checking status of values....")
        cache = _load_cache()
        app.logger.debug(f"/authorized ({Config.REDIRECT_PATH}) - token cache loaded....")
        result = _build_msal_app(cache=_load_cache(), authority=Config.AUTHORITY).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            app.logger.error(f"/authorized ({Config.REDIRECT_PATH}) - found error in result values: {result}")
            return render_template("auth_error.html", result=result)
        app.logger.debug(f"/authorized ({Config.REDIRECT_PATH}) - extracting claims...")
        session["user"] = result.get("id_token_claims")
        # Note: In a real app, we'd use the 'name' property from session["user"] below
        # Here, we'll use the admin username for anyone who is authenticated by MS
        app.logger.info(f"/authorized ({Config.REDIRECT_PATH}) - Allowing login for ADMIN account!")
        user = User.query.filter_by(username="admin").first()
        app.logger.debug(f"/authorized ({Config.REDIRECT_PATH}) - Running login_user ")
        login_user(user)
        app.logger.debug(f"/authorized ({Config.REDIRECT_PATH}) - Saving token cache")
        _save_cache(cache)
    app.logger.debug(f"/authorized ({Config.REDIRECT_PATH}) - reached end of func")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    app.logger.debug("/logout - called")
    logout_user()
    if session.get("user"): # Used MS Login
        # Wipe out user and its token cache from session
        session.clear()
        # Also logout from your tenant's web session
        return redirect(
            Config.AUTHORITY + "/oauth2/v2.0/logout" +
            "?post_logout_redirect_uri=" + url_for("login", _external=True, _scheme="https"))

    return redirect(url_for('login'))

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()
    pass

def _build_msal_app(cache=None, authority=None):
    app.logger.info(f"_build_msal_app called with {cache =} and {authority =}")
    return msal.ConfidentialClientApplication(
        client_id=Config.CLIENT_ID, authority=(authority or Config.AUTHORITY), client_credential=Config.CLIENT_SECRET, token_cache=(cache or _load_cache()))

def _build_auth_url(authority=None, scopes=None, state=None):
    app.logger.info(f"_build_auth_url called, params are {authority =} {scopes =} {state =}")
    auth_url = _build_msal_app(cache=_load_cache(), authority=(authority or Config.AUTHORITY)).get_authorization_request_url(
        scopes=scopes, redirect_uri=url_for('authorized', _external=True, _scheme = "https"))
    app.logger.info(f"_build_auth_url returning, value {auth_url =}")
    return auth_url
