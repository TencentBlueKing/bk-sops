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
    <div id="ip-selector" ref="ipSelect">
        <div class="select-area">
            <multiple-ip-selector
                v-if="isMultiple"
                ref="multipleIpSelector"
                :editable="editable"
                :selector-tabs="selectorTabs"
                :static-ip-list="staticIpList"
                :dynamic-ip-list="dynamicIpList"
                :dynamic-group-list="dynamicGroupList"
                :selectors="selectors"
                :static-ips="ip"
                :dynamic-ips="topo"
                :dynamic-groups="group"
                :manual-input="manual_input"
                @change="updateValue">
            </multiple-ip-selector>
            <single-ip-selector
                v-else
                ref="singleIpSelector"
                :editable="editable"
                :allow-unfold-input="allowUnfoldInput"
                :selector-tabs="selectorTabs"
                :static-ip-list="staticIpList"
                :dynamic-ip-list="dynamicIpList"
                :dynamic-group-list="dynamicGroupList"
                :selectors="selectors"
                :static-ips="ip"
                :dynamic-ips="topo"
                :dynamic-groups="group"
                :manual-input="manual_input"
                @change="updateValue">
            </single-ip-selector>
        </div>
        <div class="condition-area">
            <select-condition
                ref="conditions"
                :label="i18n.filterTitle"
                :editable="editable"
                :condition-fields="conditionFields"
                :conditions="conditions"
                @change="updateValue('conditions', $event)">
            </select-condition>
            <div class="cloud-area-form">
                <label :class="[editable ? '' : 'disabled']">{{ i18n.showCloudArea }}</label>
                <bk-switcher
                    size="small"
                    theme="primary"
                    :disabled="!editable"
                    v-model="with_cloud_id"
                    @change="updateValue('with_cloud_id', $event)">
                </bk-switcher>
            </div>
            <separator-select :editable="editable" :value="separator" @change="updateSeparator"></separator-select>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化
    import tools from '@/utils/tools.js'
    import SingleIpSelector from './SingleIpSelector.vue'
    import MultipleIpSelector from './MultipleIpSelector.vue'
    import SelectCondition from './SelectCondition.vue'
    import SeparatorSelect from '../SeparatorSelect.vue'

    const i18n = {
        staticIp: gettext('静态 IP'),
        dynamicIp: gettext('动态 IP'),
        dynamicGroup: gettext('动态分组'),
        manualInput: gettext('手动输入'),
        filterTitle: gettext('筛选条件和排除条件'),
        showCloudArea: gettext('变量值是否带云区域：')
    }

    // ip选择器兼容标准运维国际化
    if (typeof window.gettext !== 'function') {
        window.gettext = function gettext (string) {
            return string
        }
    }

    export default {
        name: 'IpSelector',
        components: {
            SeparatorSelect,
            SingleIpSelector,
            MultipleIpSelector,
            SelectCondition
        },
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            value: {
                type: Object,
                default () {
                    return {
                        selectors: [],
                        ip: [],
                        topo: [],
                        group: [],
                        manual_input: {},
                        filters: [],
                        excludes: [],
                        with_cloud_id: false,
                        separator: ','
                    }
                }
            },
            selectorTabs: {
                type: Array,
                default () {
                    return [
                        {
                            type: 'staticIp',
                            id: 'ip',
                            name: i18n.staticIp
                        },
                        {
                            type: 'dynamicIp',
                            id: 'topo',
                            name: i18n.dynamicIp
                        },
                        {
                            type: 'dynamicGroup',
                            id: 'group',
                            name: i18n.dynamicGroup
                        },
                        {
                            type: 'manualInput',
                            id: 'manual',
                            name: i18n.manualInput
                        }
                    ]
                }
            },
            editable: {
                type: Boolean,
                default: true
            },
            isMultiple: {
                type: Boolean,
                default: true
            },
            allowEmpty: {
                type: Boolean,
                default: true
            },
            // 静态IP可选列表
            staticIpList: {
                type: Array,
                default () {
                    return []
                }
            },
            // 动态IP可选列表
            dynamicIpList: {
                type: Array,
                default () {
                    return []
                }
            },
            // 筛选、排除条件分类
            topoModelList: {
                type: Array,
                default () {
                    return []
                }
            },
            // 动态分组可选列表(首页数据)
            dynamicGroupList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            const { selectors, ip, topo, group, filters, excludes, with_cloud_id, separator, manual_input } = this.value
            const conditions = this.getConditions(filters, excludes)
            return {
                selectors: selectors.slice(0),
                ip: ip.slice(0),
                topo: topo.slice(0),
                group: (group || []).slice(0), // 后增加字段，兼容旧数据
                manual_input: manual_input ? tools.deepClone(manual_input) : {},
                with_cloud_id,
                conditions,
                separator,
                i18n,
                allowUnfoldInput: false
            }
        },
        computed: {
            conditionFields () {
                return this.topoModelList.map(item => {
                    return {
                        id: item.bk_obj_id,
                        name: item.bk_obj_name
                    }
                })
            }
        },
        watch: {
            value: {
                handler (val) {
                    const { selectors, ip, topo, group, filters, excludes, manual_input } = this.value
                    this.selectors = selectors.slice(0)
                    this.ip = ip.slice(0)
                    this.topo = topo.slice(0)
                    this.group = (group || []).slice(0)
                    this.manual_input = manual_input ? tools.deepClone(manual_input) : {}
                    this.filters = filters.slice(0)
                    this.excludes = excludes.slice(0)
                    this.conditions = this.getConditions(filters, excludes)
                },
                deep: true
            }
        },
        mounted () {
            // ip选择器搜索框是否扩宽
            this.allowUnfoldInput = this.$refs.ipSelect.offsetWidth <= 641
            // 641为新建全局变量默认宽 不包含padding border
        },
        methods: {
            getConditions (filters, excludes) {
                const filtersArr = filters.map(item => {
                    return {
                        ...item,
                        type: 'filter'
                    }
                })
                const excludesArr = excludes.map(item => {
                    return {
                        ...item,
                        type: 'exclude'
                    }
                })
                return [...filtersArr, ...excludesArr]
            },
            updateValue (key, val) {
                if (!key) {
                    return
                }
                if (key === 'conditions') {
                    const filters = []
                    const excludes = []
                    val.forEach(item => {
                        const { field, value } = item
                        if (item.type === 'filter') {
                            filters.push({ field, value })
                        } else {
                            excludes.push({ field, value })
                        }
                    })
                    this.value.filters = filters
                    this.value.excludes = excludes
                    this.conditions = val.slice(0)
                } else {
                    if (Array.isArray(key) && Array.isArray(val)) {
                        key.forEach((k, i) => {
                            this.value[k] = val[i]
                        })
                    } else {
                        this.value[key] = val
                    }
                }

                this.$emit('change', this.value)
            },
            updateSeparator (val) {
                this.separator = val
                this.updateValue('separator', val)
            },
            validate () {
                const selector = this.isMultiple ? this.$refs.multipleIpSelector : this.$refs.singleIpSelector
                let selectorValidate = true
                if (!this.allowEmpty) {
                    selectorValidate = selector.validate()
                }
                const conditionValidate = this.$refs.conditions.validate()
            
                return selectorValidate && conditionValidate
            }
        }
    }
</script>
<style lang="scss" scoped>
.select-area {
    margin-bottom: 20px;
}
.condition-area {
    border-top: 1px dotted #c4c6cc;
}
.cloud-area-form {
    margin: 20px 0 ;
    &>label {
        font-size: 12px;
        color: #313238;
        line-height: 20px;
        &.disabled {
            color: #cccccc;
        }
    }
}
</style>
