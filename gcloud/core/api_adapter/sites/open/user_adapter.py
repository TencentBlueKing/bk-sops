# -*- coding: utf-8 -*-


def adapt_get_user_data(data):
    if 'bk_username' in data:
        data['uin'] = data.pop('bk_username')
    if 'bk_role' in data:
        data['role'] = data.pop('bk_role')
    if 'bk_supplier_account' in data:
        data.pop('bk_supplier_account')

    return data
