__author__ = 'geekscruff'

from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app
from urlparse import urlparse, urljoin

login = Blueprint('login', __name__, template_folder='templates')

@login.route('/logout', defaults={'page': 'logout'})
#this needs to be AFTER logout otherwise logout is picked up as the action for the form
@login.route('/login', defaults={'page': 'login'}, methods=['GET', 'POST'])
@login.route('/<page>')
def show(page):
    error = None
    next = get_redirect_target()
    if page == 'login':
        if request.method == 'POST':
            if request.form['username'] != current_app.config['USERNAME']:
                error = 'Invalid username'
            elif request.form['password'] != current_app.config['PASSWORD']:
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                session['user'] = request.form['username']
                flash('You were logged in')
                #return redirect(url_for('show_entries'))
                return redirect_back('login')
        return render_template('login.html', next=next, error=error)
        #return render_template('login.html', error=error)

    elif page == 'logout':
        session.pop('logged_in', None)
        flash('You were logged out')
        return redirect(url_for('home.show'))

#Securely Redirect Back By Armin Ronacher http://flask.pocoo.org/snippets/62/

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

