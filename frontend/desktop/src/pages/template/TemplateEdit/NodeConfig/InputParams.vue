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
    <div class="input-params">
        <render-form
            ref="renderForm"
            v-model="formData"
            :scheme="scheme"
            :form-option="option">
        </render-form>
        <reuse-var-dialog
            :reuse-variable="reuseVariable"
            :reuseable-var-list="reuseableVarList">
        </reuse-var-dialog>
    </div>
</template>
<script>
    import tools from '@/utils/tools.js'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import ReuseVarDialog from './ReuseVarDialog.vue'

    export default {
        name: 'InputParams',
        components: {
            RenderForm,
            ReuseVarDialog
        },
        props: {
            scheme: {
                type: Array,
                default () {
                    return []
                }
            },
            value: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                reuseVariable: {},
                reuseableVarList: [],
                formData: tools.deepClone(this.value),
                option: {
                    showGroup: false,
                    showHook: true,
                    showLabel: true,
                    showVarList: true
                }
            }
        },
        watch: {
            value (val) {
                this.formData = tools.deepClone(val)
            }
        }
    }
</script>
