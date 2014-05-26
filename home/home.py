__author__ = 'geekscruff'

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import logging
logger = logging.getLogger(__name__)

# The homepage!

home = Blueprint('home', __name__,  template_folder='templates')

@home.route('/', defaults={'page': 'index'})
@home.route('/<page>')
def show(page):
    try:
        logger.debug('DEBUG home.py - show the homepage')
        return render_template('%s.html' % page)
    except TemplateNotFound as e:
        logger.error('TemplateNotFound home.py - ' + e.message)
        abort(404)