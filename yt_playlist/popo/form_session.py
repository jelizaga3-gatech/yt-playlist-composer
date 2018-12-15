from enum import IntEnum


class FormType(IntEnum):
    default = 0
    courses = 1
    lessons = 2


class Session:
    def __init__(self, cookies, form_items, driver_url, form_type):
        self.cookies = cookies
        self.form_type = form_type
        self.driver_url = driver_url
        self.form = []
        for form_item in form_items:
            plain_item = dict(name=form_item.name,
                              radio_value=form_item.radio_value)
            self.form.append(plain_item)
