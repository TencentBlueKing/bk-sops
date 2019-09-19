/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import merge from 'webpack-merge'
import prodEnv from './prod.env'

const NODE_ENV = JSON.stringify('development')

export default merge(prodEnv, {
    'process.env': {
        'NODE_ENV': NODE_ENV
    },
    staticUrl: '/static',
    NODE_ENV: NODE_ENV,
    LOGIN_SERVICE_URL: JSON.stringify(''),
    AJAX_URL_PREFIX: JSON.stringify('http://dev.{BK_PAAS_URL}'), // 本地开发路径
    SITE_URL: JSON.stringify('')
})
