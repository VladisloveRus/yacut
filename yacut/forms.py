from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (URL, DataRequired, Length, Optional, Regexp,
                                ValidationError)

from .models import URLMap


def unique_custom_id_validator(form, field):
    field_data = field.data
    if URLMap.query.filter_by(short=field_data).first():
        raise ValidationError(f'Имя {field_data} уже занято!')
    pass


class CustomLinkForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Поле обязательно для заполнения'),
            URL(message='Убедитесь, что вставили именно ссылку'),
        ],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(1, 16, message='Не более 16 символов'),
            Regexp(
                r'^([a-zA-Z]|[0-9])*$',
                message='Только заглавные, прописные латинские буквы или цифры',
            ),
            unique_custom_id_validator,
        ],
    )
    submit = SubmitField('Создать')
