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
// Tag 配置项过滤列表
const SCHEMA_CONFIG = {
    'checkbox': null,
    'datatable': ['remote_data_init', 'remote_url'],
    'datetime': null,
    'input': ['showVarList'],
    'int': null,
    'ipSelector': null,
    'memberSelector': null,
    'password': null,
    'radio': null,
    'select': ['remote', 'remote_url', 'remote_data_init'],
    'text': null,
    'textarea': null,
    'tree': ['remote', 'remote_url', 'remote_data_init'],
    'upload': ['url', 'headers', 'auto_upload', 'limit', 'text']
}

// 过滤 tag 属性
const formSchema = {
    get (tagCode, oldConfig) {
        const { type, attrs } = oldConfig.filter(m => m.tag_code === tagCode)[0]
        const currTagFilterList = SCHEMA_CONFIG[type]
        if (!currTagFilterList) return oldConfig
        
        const newAttrs = {}
        Object.keys(attrs).forEach(key => {
            if (currTagFilterList.indexOf(key) === -1) {
                newAttrs[key] = attrs[key]
            }
        })
        const formSchema = {
            type,
            attrs: newAttrs
        }
        return formSchema
    }
}

export default formSchema
