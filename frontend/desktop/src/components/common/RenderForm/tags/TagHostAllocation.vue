/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-host-allocation">
        <span v-if="scheme.attrs.usedValue" class="rf-view-value">{{ value }}</span>
        <div class="tag-host-allocation-wrap" v-else>
            <host-allocation
                ref="hostAllocation"
                :editable="editable && !disabled"
                :view-value="!formMode"
                :urls="urls"
                :config="setValue.config"
                :separator="setValue.separator"
                :value="setValue.data"
                @update="update">
            </host-allocation>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
    import { getFormMixins } from '../formMixins.js'
    import HostAllocation from '../HostAllocation/index.vue'

    export const attrs = {
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: i18n.t('组件禁用态')
        },
        remote_url: {
            type: [Object, Function],
            required: true,
            default () {
                return {}
            },
            desc: i18n.t('组件内部调用接口地址')
        },
        value: {
            type: [Object, String],
            required: false,
            default () {
                return {
                    config: {
                        set_count: 0,
                        set_template_id: '',
                        host_resources: [],
                        module_detail: []
                    },
                    separator: '',
                    data: []
                }
            }
        }
    }
    export default {
        name: 'TagHostAllocation',
        components: {
            HostAllocation
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
                return this.$refs.hostAllocation && this.$refs.hostAllocation.validate()
            }
        }
    }
</script>
<style lang="scss" scoped>
</style>
