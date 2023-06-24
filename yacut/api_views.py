import re

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id

messages = {
    '404': 'Указанный id не найден',
    'no_data': 'Отсутствует тело запроса',
    'required_field': '\"url\" является обязательным полем!',
    'name_exists': 'Имя "{short}" уже занято.',
    'wrong_name': 'Указано недопустимое имя для короткой ссылки',
}


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_obj = URLMap.query.filter_by(short=short_id).first()
    if url_obj is None:
        raise InvalidAPIUsage(messages['404'], 404)
    url = url_obj.original
    return jsonify({'url': url}), 200


@app.route('/api/id/', methods=['POST'])
def add_url():
    data = request.get_json()
    attrs = ['original', 'short']
    fields = ['url', 'custom_id']
    if data is None:
        raise InvalidAPIUsage(messages['no_data'])
    if 'url' not in data:
        raise InvalidAPIUsage(messages['required_field'])
    url = URLMap()
    for field in fields:
        if field in data:
            setattr(url, attrs[fields.index(field)], data[field])
    if url.short is None:
        url.short = get_unique_short_id()
    if URLMap.query.filter_by(short=url.short).first() is not None:
        raise InvalidAPIUsage(messages['name_exists'].format(short=url.short))
    if (
        (
            re.fullmatch(r'^([a-zA-Z]|[0-9])*$', url.short) is None
        ) or (
            len(url.short) > 16
        )
    ):
        raise InvalidAPIUsage(messages['wrong_name'])
    db.session.add(url)
    db.session.commit()
    return (
        jsonify(
            {
                'url': url.original,
                'short_link': str(request.host_url) + str(url.short),
            }
        ),
        201,
    )
