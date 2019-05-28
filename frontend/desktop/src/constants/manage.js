/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
        name: gettext('github类型'),
        keys: {
            repo_address: gettext('仓库链接'),
            repo_raw_address: gettext('文件托管仓库链接'),
            branch: gettext('分支名')
        }
    },
    {
        type: 's3',
        name: gettext('s3类型'),
        keys: {
            service_address: gettext('对象存储服务地址'),
            bucket: gettext('bucket'),
            access_key: gettext('access_key'),
            secret_key: gettext('secret_key')
        }
    },
    {
        type: 'fs',
        name: gettext('file_system类型'),
        keys: {
            path: gettext('服务器文件系统路径')
        }
    }
]

export { SOURCE_TYPE }
