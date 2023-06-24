from random import choice
from string import ascii_letters, digits

from flask import abort, flash, redirect, render_template, request

from . import app, db
from .forms import CustomLinkForm
from .models import URLMap

DIGITS_LETTERS = list(digits) + list(ascii_letters)


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = CustomLinkForm()
    if form.validate_on_submit():
        short_link = form.custom_id.data
        if short_link is None or short_link == '':
            short_link = get_unique_short_id()
        url = URLMap(
            original=form.original_link.data,
            short=short_link,
        )
        db.session.add(url)
        db.session.commit()
        flash(str(request.host_url) + str(url.short))
    return render_template('main.html', form=form)


@app.route('/<string:short_link>')
def redirecting(short_link):
    url_obj = URLMap.query.filter_by(short=short_link).first()
    if url_obj is None:
        abort(404)
    url = url_obj.original
    return redirect(url)


def get_unique_short_id(amount=6):
    result = ''
    for _ in range(0, amount):
        result += choice(DIGITS_LETTERS)
    while URLMap.query.filter_by(short=result).first() is not None:
        result = get_unique_short_id()
    return result


if __name__ == '__main__':
    app.run()
