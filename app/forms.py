# -*- coding: utf-8 -*-
"""
    ************
    forms.py
    ************

    
"""
__author__ = 'Jonas Van Der Donckt'

from flask_wtf import FlaskForm
from wtforms import validators, RadioField, BooleanField, IntegerField, SelectField, \
    StringField


class FieldsRequiredForm(FlaskForm):
    """Require all fields to have content. This works around the bug that WTForms radio
    fields don't honor the `DataRequired` or `InputRequired` validators.

    more info see: https://github.com/wtforms/wtforms/issues/477
    """

    class Meta:
        def render_field(self, field, render_kw):
            if field.type == "_Option":
                render_kw.setdefault("required", True)
            return super().render_field(field, render_kw)


class IntroForm(FieldsRequiredForm):
    sex = RadioField('Geslacht',
                     choices=[('male', 'Man'), ('female', 'Vrouw'),
                              ('other', 'Anders')],
                     validators=[validators.DataRequired(message="Input is vereist!")])

    # todo -> fix hard coded age range
    age = IntegerField('Leeftijd',
                       validators=[validators.NumberRange(min=16, max=90,
                                                          message="Leeftijd moet tussen 16 & 90 jaar zijn"),
                                   validators.DataRequired(
                                       message="Dit is geen getal")])

    device = SelectField('Device dat je gaat gebruiken voor de audio op te nemen',
                         choices=[
                             ('pc-mic', 'microfoon van computer'),
                             ('headset', 'koptelefoon'), ('earphones', 'oortjes'),
                             ('other', 'anders')])

    accept_tos = BooleanField('Ik accepteer de informed consent', validators=[
        validators.DataRequired(message="Je moet de informed consent accepteren "
                                        "om door te gaan!")])
    prolific_token = StringField("Prolific token (optional)", default="n.a.")

    education = SelectField('Hoogst behaalde diploma', choices=[
        ('lo', 'Lager onderwijs'),
        ('so', 'Secundair onderwijs'),
        ('ho', 'Hoger onderwijs (niet universitair)'),
        ('unif', 'Universiteit')])
