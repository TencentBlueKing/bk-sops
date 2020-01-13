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
    <div id="ip-selector">
        <div class="select-area">
            <multiple-ip-selector
                v-if="isMultiple"
                ref="multipleIpSelector"
                :editable="editable"
                :selector-tabs="selectorTabs"
                :static-ip-list="staticIpList"
                :dynamic-ip-list="dynamicIpList"
                :selectors="selectors"
                :static-ips="ip"
                :dynamic-ips="topo"
                @change="updateValue">
            </multiple-ip-selector>
            <single-ip-selector
                v-else
                ref="singleIpSelector"
                :editable="editable"
                :selector-tabs="selectorTabs"
                :static-ip-list="staticIpList"
                :dynamic-ip-list="dynamicIpList"
                :selectors="selectors"
                :static-ips="ip"
                :dynamic-ips="topo"
                @change="updateValue">
            </single-ip-selector>
        </div>
        <div class="condition-area">
            <div class="cloud-area-form">
                <label>{{ i18n.showCloudArea }}</label>
                <bk-switcher
                    size="small"
                    v-model="with_cloud_id"
                    @change="updateValue('with_cloud_id', $event)">
                </bk-switcher>
            </div>
            <select-condition
                ref="filterConditions"
                :label="i18n.filter"
                :editable="editable"
                :condition-fields="topoModelList"
                :conditions="filters"
                @change="updateValue('filters', $event)">
            </select-condition>
            <select-condition
                ref="excludeConditions"
                :label="i18n.exclude"
                :editable="editable"
                :condition-fields="topoModelList"
                :conditions="excludes"
                @change="updateValue('excludes', $event)">
            </select-condition>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化
    import SingleIpSelector from './SingleIpSelector.vue'
    import MultipleIpSelector from './MultipleIpSelector.vue'
    import SelectCondition from './SelectCondition.vue'

    const i18n = {
        staticIp: gettext('静态IP'),
        dynamicIp: gettext('动态IP'),
        filter: gettext('筛选条件'),
        exclude: gettext('排除条件'),
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
                        filters: [],
                        excludes: [],
                        with_cloud_id: false
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
            }
        },
        data () {
            const { selectors, ip, topo, filters, excludes, with_cloud_id } = this.value
            return {
                selectors: selectors.slice(0),
                ip: ip.slice(0),
                topo: topo.slice(0),
                filters: filters.slice(0),
                excludes: excludes.slice(0),
                with_cloud_id,
                i18n
            }
        },
        watch: {
            value: {
                handler (val) {
                    const { selectors, ip, topo, filters, excludes } = this.value
                    this.selectors = selectors.slice(0)
                    this.ip = ip.slice(0)
                    this.topo = topo.slice(0)
                    this.filters = filters.slice(0)
                    this.excludes = excludes.slice(0)
                },
                deep: true
            }
        },
        methods: {
            updateValue (key, val) {
                if (!key) {
                    return
                }
                if (Array.isArray(key) && Array.isArray(val)) {
                    key.forEach((k, i) => {
                        this.value[k] = val[i]
                    })
                } else {
                    this.value[key] = val
                }

                this.$emit('change', this.value)
            },
            validate () {
                const selector = this.isMultiple ? this.$refs.multipleIpSelector : this.$refs.singleIpSelector
                let selectorValidate = true
                if (!this.allowEmpty) {
                    selectorValidate = selector.validate()
                }
                const filterValidate = this.$refs.filterConditions.validate()
                const excludeValidate = this.$refs.excludeConditions.validate()

                return selectorValidate && filterValidate && excludeValidate
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
    }
}
</style>
