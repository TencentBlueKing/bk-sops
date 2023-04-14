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
    <div class="tag-ip-selector" v-bkloading="{ isLoading: loading, opacity: 0.8, zIndex: 100 }">
        <div v-if="formMode && typeof ipValue === 'object'" class="tag-ip-selector-wrap">
            <ip-selector
                ref="ipSelector"
                :editable="editable && !disabled"
                :is-multiple="isMultiple"
                :selector-tabs="selectorTabs"
                :static-ip-list="staticIpList"
                :dynamic-ip-list="dynamicIpList"
                :topo-model-list="topoModelList"
                :dynamic-group-list="dynamicGroupList"
                :allow-empty="allowEmpty"
                v-model="ipValue">
            </ip-selector>
        </div>
        <span v-else class="rf-view-value">{{ constants.subflow_detail_var ? constants[tagCode] : viewValue }}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
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
            desc: i18n.t('组件禁用态')
        },
        remote_url: {
            type: [Object, Function],
            required: true,
            default: '',
            desc: i18n.t('组件内部调用接口地址')
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
    const selectorTabs = [
        {
            type: 'staticIp',
            id: 'ip',
            name: i18n.t('静态 IP'),
            hasDiff: false
        },
        {
            type: 'dynamicIp',
            id: 'topo',
            name: i18n.t('动态拓扑'),
            hasDiff: false
        },
        {
            type: 'dynamicGroup',
            id: 'group',
            name: i18n.t('动态分组'),
            hasDiff: false
        },
        {
            type: 'manualInput',
            id: 'manual',
            name: i18n.t('手动输入')
        }
    ]
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
                selectorTabs: tools.deepClone(selectorTabs),
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
                    if (selector === 'manual') {
                        val += this.ipValue['manual_input']['value']
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
                const staticIpExtraFields = ['agent', 'bk_host_innerip_v6']
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
                        let hasDiff = false
                        const value = tools.deepClone(this.value)
                        const { ip, topo, group } = value
                        values.forEach((v, index) => {
                            switch (index) {
                                case 0:
                                    this.staticIpList = v.data
                                    if (!this.hook) { // 表单没有被勾选
                                        hasDiff = ip.some(value => {
                                            // 拿到新的静态ip列表后替换对应的已保存ip属性，如果已保存ip在新列表中不存在，则提示用户手动更新
                                            return this.staticIpList.every(item => item.bk_host_id !== value.bk_host_id)
                                        })
                                        this.selectorTabs[0].hasDiff = hasDiff
                                    }
                                    break
                                case 1:
                                    this.dynamicIpList = v.data
                                    // 判断动态IP数据与最新的CMDB动态IP配置是否存在差异
                                    hasDiff = topo.every(item => {
                                        return this.loopDynamicIpList(this.dynamicIpList, item.bk_obj_id, item.bk_inst_id)
                                    })
                                    this.selectorTabs[1].hasDiff = !hasDiff
                                    break
                                case 2:
                                    this.topoModelList = v.data
                                    break
                                case 3:
                                    this.dynamicGroupList = v.data.info
                                    // 判断动态分组数据与最新的CMDB动态分组配置是否存在差异
                                    const dynamicGroups = group || []
                                    hasDiff = dynamicGroups.some(value => {
                                        return this.dynamicGroupList.every(item => item.id !== value.id)
                                    })
                                    this.selectorTabs[2].hasDiff = hasDiff
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
            loopDynamicIpList (list, objId, instId) {
                return list.some(item => {
                    if (item.bk_obj_id === objId && item.bk_inst_id === instId) {
                        return true
                    } else if (item.child && item.child.length) {
                        return this.loopDynamicIpList(item.child, objId, instId)
                    } else {
                        return false
                    }
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
