/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-ip-selector" v-bkloading="{ isLoading: loading, opacity: 0.8, zIndex: 100 }">
        <div v-if="formMode && typeof ipValue === 'object'" class="tag-ip-selector-wrap">
            <ip-selector
                ref="ipSelector"
                :editable="editable && !disabled"
                :is-multiple="isMultiple"
                :static-ip-list="staticIpList"
                :dynamic-ip-list="dynamicIpList"
                :topo-model-list="topoModelList"
                :dynamic-group-list="dynamicGroupList"
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
    import tools from '@/utils/tools.js'
    import { getFormMixins } from '../formMixins.js'
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
                    with_cloud_id: false,
                    separator: ','
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
                loading: false,
                isvalidate: false,
                staticIpList: [],
                dynamicIpList: [],
                topoModelList: [],
                dynamicGroupList: [] // 动态分组的首页数据，如果大于 200 条，在组件内部单独请求
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
                'getTopoModelInCC',
                'getDynamicGroup'
            ]),
            getData () {
                const staticIpExtraFields = ['agent']
                const urls = typeof this.remote_url === 'function' ? this.remote_url() : Object.assign({}, this.remote_url)
                if (!urls['cc_search_host'] || !urls['cc_search_topo_tree'] || !urls['cc_get_mainline_object_topo']) {
                    return
                }
                this.loading = true
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
                    }),
                    this.getDynamicGroup({
                        url: urls['cc_dynamic_group_list']
                    })
                ]).then(values => {
                    if (Array.isArray(values)) {
                        values.forEach((v, index) => {
                            switch (index) {
                                case 0:
                                    this.staticIpList = v.data
                                    if (!this.hook) { // 表单没有被勾选
                                        const value = tools.deepClone(this.value)
                                        const ips = []
                                        value.ip.forEach(item => {
                                            // 拿到新的静态ip列表后替换对应的已保存ip属性，如果已保存ip在新列表中不存在，则过滤掉
                                            const ipItem = this.staticIpList.find(i => i.bk_host_innerip === item.bk_host_innerip)
                                            if (ipItem) {
                                                ips.push(tools.deepClone(ipItem))
                                            }
                                        })
                                        value.ip = ips
                                        this.updateForm(value)
                                    }
                                    break
                                case 1:
                                    this.dynamicIpList = v.data
                                    break
                                case 2:
                                    this.topoModelList = v.data
                                    break
                                case 3:
                                    this.dynamicGroupList = v.data.info
                                    break
                            }
                        })
                    }
                    this.loading = false
                }).catch(e => {
                    this.loading = false
                    console.log(e)
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
