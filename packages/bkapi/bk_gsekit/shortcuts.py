# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import generic_type_partial as _partial
from bkapi_client_core.apigateway.django_helper import get_client_by_request as _get_client_by_request
from bkapi_client_core.apigateway.django_helper import get_client_by_username as _get_client_by_username

from .client import Client

get_client_by_request = _partial(Client, _get_client_by_request)
get_client_by_username = _partial(Client, _get_client_by_username)
