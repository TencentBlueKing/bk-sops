/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/

// 包源类型
const SOURCE_TYPE = [
    {
        type: 'git',
        name: gettext('GIT'),
        keys: {
            repo_address: {
                name: gettext('仓库链接'),
                placeholder: gettext('请输入 GIT 仓库地址，如 https://github.com/bk-sops/plugins_example.git')
            },
            repo_raw_address: {
                name: gettext('文件托管仓库链接'),
                placeholder: gettext('请输入仓库中文件的 Raw 链接的前缀，如 https://raw.githubusercontent.com/bk-sops/plugins_example/')
            },
            branch: {
                name: gettext('分支名'),
                placeholder: gettext('请输入分支名')
            }
        }
    },
    {
        type: 's3',
        name: gettext('S3'),
        keys: {
            service_address: {
                name: gettext('对象存储服务地址'),
                placeholder: gettext('请输入')
            },
            bucket: {
                name: gettext('Bucket'),
                placeholder: gettext('请输入')
            },
            access_key: {
                name: gettext('Access Key'),
                placeholder: gettext('请输入')
            },
            secret_key: {
                name: gettext('Secret Key'),
                placeholder: gettext('请输入')
            }
        }
    },
    {
        type: 'fs',
        name: gettext('文件系统'),
        keys: {
            path: {
                name: gettext('服务器文件系统路径'),
                placeholder: gettext('请输入')
            }
        }
    }
]

export { SOURCE_TYPE }
