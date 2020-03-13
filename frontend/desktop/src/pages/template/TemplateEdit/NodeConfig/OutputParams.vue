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
<template>
    <div class="output-params">
        <bk-table :data="params" :border="true">
            <bk-table-column :label="i18n.name" :width="250" align="center" prop="name"></bk-table-column>
            <bk-table-column label="KEY" align="center" prop="key"></bk-table-column>
            <bk-table-column :label="i18n.cite" :width="100" align="center">
                <template slot-scope="props">
                    <bk-checkbox @change="onToggleCheck(props)"></bk-checkbox>
                </template>
            </bk-table-column>
        </bk-table>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'OutputParams',
        props: {
            params: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                i18n: {
                    name: gettext('名称'),
                    cite: gettext('引用')
                }
            }
        },
        methods: {
            onToggleCheck () {}
        }
    }
</script>
