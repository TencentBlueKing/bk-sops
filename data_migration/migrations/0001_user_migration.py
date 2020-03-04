# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import unicode_literals

import sys


import django.utils.timezone
import django.core.validators
from django.conf import settings as django_settings
from django.db import migrations, connection, transaction, models
from django.db.migrations.recorder import MigrationRecorder

from data_migration.conf import settings
from data_migration.utils import dictfetchall, old_uer_table_exist

additional_key = settings.USER_ADDITIONAL_PROPERTY
fields_map = settings.USER_FIELDS_MAP


class BKAccountCreateModel(migrations.CreateModel):
    def state_forwards(self, app_label, state):
        state.add_model(ModelState(
            'account',
            self.name,
            list(self.fields),
            dict(self.options),
            tuple(self.bases),
            list(self.managers),
        ))

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model('account', self.name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.create_model(model)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model('account', self.name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.delete_model(model)


class BKAccountAlterUniqueTogether(migrations.AlterUniqueTogether):
    def state_forwards(self, app_label, state):
        model_state = state.models['account', self.name_lower]
        model_state.options[self.option_name] = self.unique_together
        state.reload_model('account', self.name_lower, delay=True)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        new_model = to_state.apps.get_model('account', self.name)
        if self.allow_migrate_model(schema_editor.connection.alias, new_model):
            old_model = from_state.apps.get_model('account', self.name)
            schema_editor.alter_unique_together(
                new_model,
                getattr(old_model._meta, self.option_name, set()),
                getattr(new_model._meta, self.option_name, set()),
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        return self.database_forwards('account', schema_editor, from_state, to_state)


def reverse_func(apps, schema_editor):
    if not old_uer_table_exist():
        return

    User = apps.get_model('account', 'User')
    UserProperty = apps.get_model('account', 'UserProperty')

    db_alias = schema_editor.connection.alias
    with transaction.atomic():
        UserProperty.objects.using(db_alias).all().delete()
        User.objects.using(db_alias).all().delete()


def forward_func(apps, schema_editor):
    if not old_uer_table_exist():
        return

    User = apps.get_model('account', 'User')
    UserProperty = apps.get_model('account', 'UserProperty')

    db_alias = schema_editor.connection.alias
    with connection.cursor() as cursor:
        cursor.execute('select * from %s'
                       % getattr(settings, 'USER_TABLE', 'account_bkuser'))
        bk_users = dictfetchall(cursor)
        cursor.execute('select * from %s'
                       % getattr(settings, 'USER_GROUP_TABLE', 'account_bkuser_groups'))
        groups = dictfetchall(cursor)
        cursor.execute('select * from %s'
                       % getattr(settings, 'USER_PERMISSION_TABLE', 'account_bkuser_user_permissions'))
        permissions = dictfetchall(cursor)

    users = []
    user_properties = []

    for row in bk_users:

        try:
            user = User.objects.using(db_alias).get(username=row['username'])
        except Exception:
            user = User(
                id=row[fields_map['id']],
                username=row[fields_map['username']],
                nickname=row[fields_map['nickname']],
                is_staff=row[fields_map['is_staff']],
                is_active=True,
                is_superuser=row[fields_map['is_superuser']],
                date_joined=row[fields_map['date_joined']]
            )
            users.append(user)

        for key in additional_key:
            user_properties.append(
                UserProperty(
                    user=user,
                    key=key,
                    value=row[key] or ''
                )
            )

    group_values = []
    for row in groups:
        group_values.append('(%s, %s, %s)' %
                            (row['id'], row['bkuser_id'], row['group_id']))

    permission_values = []
    for row in permissions:
        permission_values.append('(%s, %s, %s)' % (
            row['id'], row['bkuser_id'], row['permission_id']))

    with transaction.atomic():
        User.objects.bulk_create(users)
        UserProperty.objects.bulk_create(user_properties)
        with connection.cursor() as cursor:
            if group_values:
                cursor.execute('insert into `account_user_groups` (id, user_id, group_id) values %s;' %
                               ','.join(group_values))
            if permission_values:
                cursor.execute('insert into `account_user_permissions` (id, user_id, permission_id) values %s;' %
                               ','.join(permission_values))


class Migration(migrations.Migration):

    model_operations = [
        BKAccountCreateModel(
            name='User',
            fields=[
                ('id',
                 models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(
                    max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(
                    blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False,
                                                     help_text='Designates that this user has all permissions without explicitly assigning them.',
                                                     verbose_name='superuser status')),
                ('username',
                 models.CharField(error_messages={'unique': 'A user with that openid already exists.'},
                                  help_text='Required. 64 characters or fewer. Letters, digits and underlined only.',
                                  max_length=64, unique=True, validators=[
                     django.core.validators.RegexValidator('^[a-zA-Z0-9_]+$',
                                                           'Enter a valid openid. This value may contain only letters, numbers and underlined characters.',
                                                           'invalid')], verbose_name='username')),
                ('nickname',
                 models.CharField(blank=True, help_text='Required. 64 characters or fewer.', max_length=64,
                                  verbose_name='nick name')),
                ('is_staff', models.BooleanField(default=False,
                                                 help_text='Designates whether the user can log into this admin site.',
                                                 verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True,
                                                  help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                                                  verbose_name='active')),
                ('date_joined',
                 models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True,
                                                  help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                                  related_name='user_set', related_query_name='user',
                                                  to='auth.Group', verbose_name='groups')),
                ('user_permissions',
                 models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                                        related_name='user_set', related_query_name='user',
                                        to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        BKAccountCreateModel(
            name='UserProperty',
            fields=[
                ('id',
                 models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(
                    help_text='Required. 64 characters or fewer. Letters, digits and underlined only.',
                    max_length=64, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9_]+$',
                                                                                     'Enter a valid key. This value may contain only letters, numbers and underlined characters.',
                                                                                     'invalid')])),
                ('value', models.TextField()),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties',
                                   to=django_settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_user_property',
                'verbose_name': 'user property',
                'verbose_name_plural': 'user properties',
            },
        ),
        BKAccountCreateModel(
            name='UserProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('account.user',),
        ),
        BKAccountAlterUniqueTogether(
            name='userproperty',
            unique_together=set([('user', 'key')]),
        ),
    ]

    data_operations = [
        migrations.RunPython(forward_func, reverse_func)
    ]

    operations = []

    def apply(self, project_state, schema_editor, collect_sql=False):
        with connection.cursor() as cursor:
            recorder = MigrationRecorder(connection)
            applied = recorder.applied_migrations()
            for migration in applied:
                if migration[0] == 'account' and migration[1] == '0001_initial':
                    sys.stdout.write('add account model initial operations')
                    self.operations.extend(self.model_operations)

        self.operations.extend(self.data_operations)
        return super(Migration, self).apply(project_state, schema_editor, collect_sql)
