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
    <div class="single-ip-selector">
        <div :class="['selector-choose-wrap', { 'disabled': !editable }]">
            <div
                v-for="(selector) in selectorTabs"
                :key="selector.type"
                :class="['ip-tab-radio', { 'disabled': !editable }]"
                @click="onChooseSelector(selector)">
                <span :class="['radio', { 'checked': activeSelector === selector.id }]"></span>
                <span class="radio-text">{{selector.name}}</span>
            </div>
        </div>
        <bk-alert
            v-if="curSelectorTab.hasDiff"
            ref="diffAlert"
            type="warning"
            style="margin-bottom: 10px;"
            :class="{ 'alert-disabled': !editable }"
            :show-icon="false">
            <div class="diff-alert" slot="title">
                <span>{{ $t('表单保存数据与最新的CMDB') + curSelectorTab.name.replace(/\s/, '') + $t('配置存在差异，是否更新变量数据？') }}</span>
                <bk-link theme="primary" @click="updateDiffData">{{ $t('确认') }}</bk-link>
            </div>
        </bk-alert>
        <div class="selector-content">
            <static-ip
                v-show="activeSelector === 'ip'"
                ref="ip"
                :allow-unfold-input="allowUnfoldInput"
                :editable="editable"
                :static-ip-list="staticIpList"
                :static-ips="staticIps"
                :static-ip-table-config="staticIpTableConfig"
                @onTableConfigChange="onStaticIpTableSettingChange"
                @change="onStaticIpChange">
            </static-ip>
            <dynamic-ip
                v-show="activeSelector === 'topo'"
                ref="topo"
                :editable="editable"
                :dynamic-ip-list="dynamicIpList"
                :dynamic-ips="dynamicIps"
                @change="onDynamicIpChange">
            </dynamic-ip>
            <dynamic-group
                v-show="activeSelector === 'group'"
                ref="group"
                :editable="editable"
                :dynamic-group-list="dynamicGroupList"
                :dynamic-groups="dynamicGroups"
                @change="onDynamicGroupChange">
            </dynamic-group>
            <manual-input
                v-show="activeSelector === 'manual'"
                ref="manual"
                :editable="editable"
                :selector-tabs="selectorTabs"
                :manual-input="manualInput"
                @change="onManualInputChange">
            </manual-input>
        </div>
    </div>
</template>
<script>
    import StaticIp from './StaticIp.vue'
    import DynamicIp from './DynamicIp.vue'
    import DynamicGroup from './DynamicGroup.vue'
    import ManualInput from './ManualInput'

    export default {
        name: 'SingleIpSelector',
        components: {
            StaticIp,
            DynamicIp,
            DynamicGroup,
            ManualInput
        },
        props: {
            allowUnfoldInput: Boolean,
            editable: Boolean,
            selectorTabs: Array,
            selectors: Array,
            staticIpList: Array,
            dynamicIpList: Array,
            dynamicGroupList: Array,
            staticIpTableConfig: Array,
            staticIps: Array,
            dynamicIps: Array,
            dynamicGroups: Array,
            manualInput: Object
        },
        data () {
            return {
                activeSelector: this.selectors[0],
                curSelectorTab: {}
            }
        },
        watch: {
            selectorTabs: {
                handler (tabs) {
                    const curSelectorTab = tabs.find(item => item.id === this.activeSelector)
                    this.curSelectorTab = curSelectorTab
                },
                immediate: true
            },
            selectors (val, oldVal) {
                if (val.toString() !== oldVal.toString()) {
                    this.activeSelector = val[0]
                    this.curSelectorTab = this.selectorTabs.find(item => item.id === val[0])
                }
            }
        },
        methods: {
            onChooseSelector (selector) {
                if (!this.editable) {
                    return
                }
                this.curSelectorTab = selector
                this.$emit('change', 'selectors', [selector.id])
            },
            updateDiffData () {
                if (!this.editable) return
                const selectors = this.activeSelector
                let selectList = selectors === 'ip' ? this.staticIps : selectors === 'topo' ? this.dynamicIps : this.dynamicGroups
                selectList = selectList.filter((value, index) => {
                    let result = true
                    // 删除掉没匹配上的
                    if (selectors === 'ip') {
                        result = this.staticIpList.find(item => item.bk_host_id === value.bk_host_id)
                    } else if (selectors === 'topo') {
                        result = this.loopDynamicIpList(this.dynamicIpList, value.bk_obj_id, value.bk_inst_id)
                    } else {
                        result = this.dynamicGroupList.find(item => item.id === value.id)
                    }
                    return result
                })
                this.$emit('change', selectors, selectList)
                this.curSelectorTab.hasDiff = false
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
            onStaticIpTableSettingChange (val) {
                this.$emit('change', 'static_ip_table_config', val)
            },
            onStaticIpChange (val) {
                this.$emit('change', 'ip', val)
            },
            onDynamicIpChange (val) {
                this.$emit('change', 'topo', val)
            },
            onDynamicGroupChange (val) {
                this.$emit('change', 'group', val)
            },
            onManualInputChange (val) {
                this.$emit('change', 'manual_input', val)
            },
            validate () {
                return this.$refs[this.activeSelector].validate()
            }
        }
    }
</script>
<style lang="scss" scoped>
.ip-tab-radio {
    display: inline-block;
    font-size: 14px;
    height: 42px;
    margin-right: 30px;
    cursor: pointer;
    .radio-box {
        display: flex;
    }
    .radio {
        display: inline-block;
        position: relative;
        width: 16px;
        height: 16px;
        margin: 12px 0;
        border: 1px solid #c4c6cc;
        border-radius: 50%;
        vertical-align: middle;
        &.checked {
            border-color: #3a84ff;
            &:before {
                content: '';
                position: absolute;
                top: 3px;
                right: 3px;
                width: 8px;
                height: 8px;
                background: #3a84ff;
                border-radius: 50%;
            }
        }
    }
    &.disabled {
        color: #cccccc;
        cursor: not-allowed;
        .radio {
            background: #fafbfd;
            border-color: #dcdee5;
            &.checked:before {
                background: #cccccc;
            }
        }
    }
}
.diff-alert {
    display: flex;
    justify-content: space-between;
    align-items: center;
    /deep/ .bk-link-text {
        font-size: 12px;
    }
}
.alert-disabled {
    color: #ccc;
    cursor: not-allowed;
    /deep/ .bk-link-text {
        color: #ccc;
        cursor: not-allowed;
    }
}
</style>
