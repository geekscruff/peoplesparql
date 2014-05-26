__author__ = 'geekscruff'

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import logging
logger = logging.getLogger(__name__)

# The project page!

project = Blueprint('project', __name__, template_folder='templates')

@project.route('/project', defaults={'page': 'project'})
@project.route('/<page>')
def show(page):
    try:
        logger.debug('DEBUG project.py - show the project page')
        return render_template('project/%s.html' % page)
    except TemplateNotFound as e:
        logger.error('TemplateNotFound project.py - ' + e.message)
        abort(404)