from django import template
from django.utils.formats import date_format

import datetime
from urllib.parse import urlencode
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

register = template.Library()


@register.simple_tag()
def thousand_sep(number, round_rate=0):
    try:
        number = float(number)
        lol = '{:,.' + str(round_rate) + 'f}'
        number = lol.format(round(number, round_rate)).replace(',', u"\u00A0")
    except:
        pass

    return number


@register.simple_tag
def date_standart(value, source_format="%Y-%m-%d", export_format="j E Y года"):
    try:
        value = value.split("T")[0]

        if bool(value.strip()):
            return date_format(datetime.datetime.strptime(value, source_format), format=export_format, use_l10n=True)
        else:
            return '—'
    except :
        return '—'

@register.simple_tag
def get_word_after_num(word, num):
    word = morph.parse(word)[0]
    new_word = word.make_agree_with_number(int(num)).word
    return str(num) + " " + new_word
