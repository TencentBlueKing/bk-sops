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
<template>
    <div class="tag-set-allocation">
        <div class="tag-set-allocation-wrap">
            <set-allocation
                ref="setAllocation"
                :editable="editable && !disabled"
                :view-value="!formMode"
                :urls="urls"
                :config="setValue.config"
                :value="setValue.data"
                @update="update">
            </set-allocation>
        </div>
    </div>
</template>
<script>
    import '../utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'
    import SetAllocation from '../components/SetAllocation/index.vue'

    export const attrs = {
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: gettext('组件禁用态')
        },
        remote_url: {
            type: [Object, Function],
            required: true,
            default () {
                return {}
            },
            desc: gettext('组件内部调用接口地址')
        },
        value: {
            type: [Object, String],
            required: false,
            default () {
                return {
                    config: {},
                    data: {}
                }
            }
        }
    }
    export default {
        name: 'TagSetAllocation',
        components: {
            SetAllocation
        },
        mixins: [getFormMixins(attrs)],
        computed: {
            urls () {
                return typeof this.remote_url === 'function' ? this.remote_url() : Object.assign({}, this.remote_url)
            },
            setValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            }
        },
        methods: {
            update (val) {
                this.setValue = val
            },
            customValidate () {
                return this.$refs.setAllocation && this.$refs.setAllocation.validate()
            }
        }
    }
</script>
<style lang="scss" scoped>
</style>
