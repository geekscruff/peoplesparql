__author__ = 'geekscruff'

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

project = Blueprint('project', __name__,
                        template_folder='templates')

@project.route('/project', defaults={'page': 'project'})
@project.route('/blog', defaults={'page': 'blog'})
@project.route('/<page>')
def show(page):
    try:
        return render_template('project/%s.html' % page)
    except TemplateNotFound:
        abort(404)