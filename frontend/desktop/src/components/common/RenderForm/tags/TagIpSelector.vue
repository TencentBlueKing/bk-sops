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
        <span v-if="scheme.attrs.usedValue" class="rf-view-value">{{ value }}</span>
        <div v-else-if="typeof ipValue === 'object'" class="tag-ip-selector-wrap">
            <ip-selector
                ref="ipSelector"
                :editable="editable && !disabled"
                :is-multiple="isMultiple"
                :selector-tabs="selectorTabs"
                :dynamic-ip-list="dynamicIpList"
                :topo-model-list="topoModelList"
                :dynamic-group-list="dynamicGroupList"
                :allow-empty="allowEmpty"
                v-model="ipValue">
            </ip-selector>
        </div>
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
            load: false
        },
        {
            type: 'dynamicIp',
            id: 'topo',
            name: i18n.t('动态拓扑'),
            load: false
        },
        {
            type: 'dynamicGroup',
            id: 'group',
            name: i18n.t('动态分组'),
            load: false
        },
        {
            type: 'manualInput',
            id: 'manual',
            name: i18n.t('手动输入'),
            load: false
        }
    ]
    export default {
        name: 'TagIpSelector',
        components: {
            IpSelector
        },
        mixins: [getFormMixins(attrs)],
        provide () {
            return {
                remoteUrl: this.remote_url
            }
        },
        data () {
            return {
                loading: false,
                isvalidate: false,
                selectorTabs: tools.deepClone(selectorTabs),
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
        watch: {
            'ipValue.selectors': {
                handler (val, oldVal) {
                    if (!val.length || tools.isDataEqual(val, oldVal)) return
                    this.getData()
                },
                immediate: true
            }
        },
        methods: {
            ...mapActions([
                'getHostInCC',
                'getTopoTreeInCC',
                'getTopoModelInCC',
                'getDynamicGroup'
            ]),
            getData () {
                // 只展示文本时无需发起请求
                if (this.scheme.attrs.usedValue) return

                const staticIpExtraFields = ['agent', 'bk_host_innerip_v6']
                const urls = typeof this.remote_url === 'function' ? this.remote_url() : Object.assign({}, this.remote_url)
                if (!urls['cc_search_host'] || !urls['cc_search_topo_tree'] || !urls['cc_get_mainline_object_topo']) {
                    return
                }
                // 已经加载的tab，无需再次请求接口
                const selectorInfo = this.selectorTabs.find(item => item.id === this.ipValue.selectors[0])
                if (selectorInfo.load) return

                this.loading = true
                const requestList = []
                switch (selectorInfo.id) {
                    case 'ip':
                        // 该接口默认不调，如果有ip已经选中了则过滤出对应的host_id列表
                        if (this.value.ip.length) {
                            const hostIds = this.value.ip.map(item => item.bk_host_id).join(',')
                            requestList.push(this.getHostInCC({
                                url: urls['cc_search_host'],
                                fields: staticIpExtraFields,
                                host_id_str: hostIds || undefined
                            }))
                        }
                        break
                    case 'topo':
                        requestList.push(this.getTopoTreeInCC({ url: urls['cc_search_topo_tree'] }))
                        break
                    case 'group':
                        requestList.push(this.getDynamicGroup({ url: urls['cc_dynamic_group_list'] }))
                        break
                }
                // 这个接口只在初始化的时候调一次
                const isInit = this.selectorTabs.every(item => !item.load)
                if (isInit) {
                    requestList.push(this.getTopoModelInCC({ url: urls['cc_get_mainline_object_topo'] }))
                }

                Promise.all(requestList).then(values => {
                    let hasDiff = false
                    const { ip, group } = this.value
                    values.forEach((v, index) => {
                        if (index === 0) {
                            switch (selectorInfo.id) {
                                case 'ip':
                                    if (!this.hook) { // 表单没有被勾选
                                        ip.forEach(value => {
                                            // 拿到新的静态ip列表后替换对应的已保存ip属性，如果已保存ip在新列表中不存在，则提示用户手动更新
                                            hasDiff = v.data.every(item => item.bk_host_id !== value.bk_host_id)
                                            this.$set(value, 'diff', hasDiff)
                                        })
                                    }
                                    break
                                case 'topo':
                                    this.dynamicIpList = v.data
                                    break
                                case 'group':
                                    this.dynamicGroupList = v.data.info
                                    // 判断动态分组数据与最新的CMDB动态分组配置是否存在差异
                                    const dynamicGroups = group || []
                                    dynamicGroups.some(value => {
                                        hasDiff = this.dynamicGroupList.every(item => item.id !== value.id)
                                        this.$set(value, 'diff', hasDiff)
                                    })
                                    break
                                default:
                                    this.topoModelList = v.data
                                    break
                            }
                        } else {
                            this.topoModelList = v.data
                        }
                    })
                    this.loading = false
                    selectorInfo.load = true
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
