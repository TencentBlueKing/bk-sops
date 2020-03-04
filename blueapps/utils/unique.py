# -*- coding: utf-8 -*-

import uuid


def uniqid():
    return uuid.uuid3(
        uuid.uuid1(),
        uuid.uuid4().hex
    ).hex
