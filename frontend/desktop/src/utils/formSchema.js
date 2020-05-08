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
/**
 * 参数 schema 是用于描述标准运维流程模板中输入类型全局变量的元信息的结构，
 * 其记录了全局变量的 类型， 可选值， 结构， 描述 等信息，目的是方便 API 的调用方获取模板中全局变量的相关信息。
 * 目前流程模板中输入类型的全局变量来源有以下两种：
 * 插件表单中勾选
 * 自定义全局变量
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
    /**
     * 获取 form_schema
     * @param {String} tagCode tag_code
     * @param {Object} oldConfig 原始配置
     */
    getSchema (tagCode, oldConfig) {
        const config = oldConfig.find(m => m.tag_code === tagCode)
        if (!config) {
            return {}
        }
        const { type, attrs } = config
        const currTagFilterList = SCHEMA_CONFIG[type]
        const newAttrs = {}

        if (!currTagFilterList) return { type, attrs }
        Object.keys(attrs).forEach(key => {
            if (currTagFilterList.indexOf(key) === -1) {
                newAttrs[key] = attrs[key]
            }
        })
        return {
            type,
            attrs: newAttrs
        }
    }
}

export default formSchema
