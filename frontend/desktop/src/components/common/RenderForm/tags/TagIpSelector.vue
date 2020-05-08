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
<template>
    <div class="tag-ip-selector" v-bkloading="{ isLoading: loading, opacity: 0.8 }">
        <div v-if="formMode && typeof ipValue === 'object'" class="tag-ip-selector-wrap">
            <ip-selector
                ref="ipSelector"
                :editable="editable && !disabled"
                :is-multiple="isMultiple"
                :static-ip-list="staticIpList"
                :dynamic-ip-list="dynamicIpList"
                :topo-model-list="topoModelList"
                :allow-empty="allowEmpty"
                v-model="ipValue">
            </ip-selector>
        </div>
        <span v-else class="rf-view-value">{{viewValue}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { getFormMixins } from '../formMixins.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import IpSelector from '../IpSelector/index.vue'

    export const attrs = {
        isMultiple: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'checkbox or radio'
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: gettext('组件禁用态')
        },
        remote_url: {
            type: [Object, Function],
            required: true,
            default: '',
            desc: gettext('组件内部调用接口地址')
        },
        value: {
            type: [Object, String],
            required: false,
            default () {
                return {
                    selectors: ['ip'],
                    ip: [],
                    topo: [],
                    filters: [],
                    excludes: [],
                    with_cloud_id: false
                }
            }
        }
    }
    export default {
        name: 'TagIpSelector',
        components: {
            IpSelector
        },
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                loading: true,
                isvalidate: false,
                staticIpList: [],
                dynamicIpList: [],
                topoModelList: []
            }
        },
        computed: {
            ipValue: {
                get () {
                    return this.value
                },
                set (val) {
                    // 验证后更新
                    this.updateForm(val)
                }
            },
            viewValue () {
                let val = ''
                this.ipValue.selectors && this.ipValue.selectors.forEach(selector => {
                    if (selector === 'ip') {
                        val += this.ipValue[selector].map(item => item.bk_host_innerip).join('; ')
                    }
                    if (selector === 'topo') {
                        val += this.ipValue[selector].map(item => item.bk_inst_id).join('; ')
                    }
                })
                return val || '--'
            },
            allowEmpty () {
                return !this.validateSet.includes('required')
            }
        },
        mounted () {
            this.getData()
        },
        methods: {
            ...mapActions([
                'getHostInCC',
                'getTopoTreeInCC',
                'getTopoModelInCC'
            ]),
            getData () {
                this.loading = true
                const staticIpExtraFields = ['agent']
                const urls = typeof this.remote_url === 'function' ? this.remote_url() : Object.assign({}, this.remote_url)
                Promise.all([
                    this.getHostInCC({
                        url: urls['cc_search_host'],
                        fields: staticIpExtraFields
                    }),
                    this.getTopoTreeInCC({
                        url: urls['cc_search_topo_tree']
                    }),
                    this.getTopoModelInCC({
                        url: urls['cc_get_mainline_object_topo']
                    })
                ]).then(values => {
                    if (Array.isArray(values)) {
                        this.staticIpList = (values[0] && values[0].data) || []
                        this.dynamicIpList = (values[1] && values[1].data) || []
                        this.topoModelList = (values[2] && values[2].data) || []
                    }
                    this.loading = false
                }).catch(e => {
                    this.loading = false
                    errorHandler(e, this)
                })
            },
            customValidate () {
                return this.$refs.ipSelector && this.$refs.ipSelector.validate()
            }
        }
    }
</script>
<style lang="scss" scoped>
.tag-ip-selector-wrap {
    padding: 10px;
    border: 1px solid #dcdee5;
}
</style>
