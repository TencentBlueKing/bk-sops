# -*- coding: utf-8 -*-
#
# import logging
# from django.test import TestCase
#
# from pipeline.component_framework.test import ComponentTestCase
#
# logger = logging.getLogger('root')
#
#
# class JobFastExecuteSqlComponentTest(TestCase, ComponentTestCase):
#     @property
#     def cases(self):
#         return [
#             ComponentTestCase(name='success case', inputs={'job_content': 'show databases;',
#                                                            'job_script_source': 'manual',
#                                                            'db_account_id': '1',
#                                                            'job_ip_list': '172.19.6.9'},
#                               parent_data={'': ''})
#         ]
