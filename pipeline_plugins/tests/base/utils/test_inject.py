# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.base.utils.inject import (
    supplier_account_for_business,
    supplier_account_for_project,
    supplier_account_inject,
    supplier_id_for_business,
    supplier_id_for_project,
    supplier_id_inject,
)


class InjectTestCase(TestCase):
    @patch("pipeline_plugins.base.utils.inject.Project")
    @patch("pipeline_plugins.base.utils.inject.supplier_account_for_business")
    def test_supplier_account_for_project(self, mock_account_for_biz, mock_project):
        # Case 1: Project exists and from_cmdb is True
        mock_proj = MagicMock()
        mock_proj.from_cmdb = True
        mock_proj.bk_biz_id = 1
        mock_project.objects.get.return_value = mock_proj
        mock_account_for_biz.return_value = 100

        self.assertEqual(supplier_account_for_project(1), 100)

        # Case 2: Project does not exist
        mock_project.DoesNotExist = Exception
        mock_project.objects.get.side_effect = Exception
        self.assertEqual(supplier_account_for_project(1), 0)

        # Case 3: Project exists but from_cmdb is False
        mock_project.objects.get.side_effect = None
        mock_proj.from_cmdb = False
        mock_project.objects.get.return_value = mock_proj
        self.assertEqual(supplier_account_for_project(1), 0)

    @patch("pipeline_plugins.base.utils.inject.Business")
    def test_supplier_account_for_business(self, mock_business):
        # Case 1: Business exists
        mock_business.objects.supplier_account_for_business.return_value = 100
        self.assertEqual(supplier_account_for_business(1), 100)

        # Case 2: Business does not exist
        mock_business.DoesNotExist = Exception
        mock_business.objects.supplier_account_for_business.side_effect = Exception
        self.assertEqual(supplier_account_for_business(1), 0)

    @patch("pipeline_plugins.base.utils.inject.Project")
    @patch("pipeline_plugins.base.utils.inject.supplier_id_for_business")
    def test_supplier_id_for_project(self, mock_id_for_biz, mock_project):
        # Case 1: Project exists and from_cmdb is True
        mock_proj = MagicMock()
        mock_proj.from_cmdb = True
        mock_proj.bk_biz_id = 1
        mock_project.objects.get.return_value = mock_proj
        mock_id_for_biz.return_value = 100

        self.assertEqual(supplier_id_for_project(1), 100)

        # Case 2: Project does not exist
        mock_project.DoesNotExist = Exception
        mock_project.objects.get.side_effect = Exception
        self.assertEqual(supplier_id_for_project(1), 0)

        # Case 3: Project exists but from_cmdb is False
        mock_project.objects.get.side_effect = None
        mock_proj.from_cmdb = False
        mock_project.objects.get.return_value = mock_proj
        self.assertEqual(supplier_id_for_project(1), 0)

    @patch("pipeline_plugins.base.utils.inject.Business")
    def test_supplier_id_for_business(self, mock_business):
        # Case 1: Business exists
        mock_business.objects.supplier_id_for_business.return_value = 100
        self.assertEqual(supplier_id_for_business(1), 100)

        # Case 2: Business does not exist
        mock_business.DoesNotExist = Exception
        mock_business.objects.supplier_id_for_business.side_effect = Exception
        self.assertEqual(supplier_id_for_business(1), 0)

    @patch("pipeline_plugins.base.utils.inject.supplier_account_for_project")
    @patch("pipeline_plugins.base.utils.inject.supplier_account_for_business")
    def test_supplier_account_inject(self, mock_for_biz, mock_for_proj):
        @supplier_account_inject
        def func(*args, **kwargs):
            return kwargs.get("supplier_account")

        # Case 1: project_id
        mock_for_proj.return_value = 10
        self.assertEqual(func(project_id=1), 10)

        # Case 2: biz_cc_id
        mock_for_biz.return_value = 20
        self.assertEqual(func(biz_cc_id=1), 20)

        # Case 3: bk_biz_id
        mock_for_biz.return_value = 30
        self.assertEqual(func(bk_biz_id=1), 30)

        # Case 4: No id
        self.assertIsNone(func())

    @patch("pipeline_plugins.base.utils.inject.supplier_id_for_project")
    @patch("pipeline_plugins.base.utils.inject.supplier_id_for_business")
    def test_supplier_id_inject(self, mock_for_biz, mock_for_proj):
        @supplier_id_inject
        def func(*args, **kwargs):
            return kwargs.get("supplier_id")

        # Case 1: project_id
        mock_for_proj.return_value = 10
        self.assertEqual(func(project_id=1), 10)

        # Case 2: biz_cc_id
        mock_for_biz.return_value = 20
        self.assertEqual(func(biz_cc_id=1), 20)

        # Case 3: bk_biz_id
        mock_for_biz.return_value = 30
        self.assertEqual(func(bk_biz_id=1), 30)

        # Case 4: No id
        self.assertIsNone(func())
