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
    <div class="single-ip-selector">
        <div :class="['selector-choose-wrap', { 'disabled': !editable }]">
            <div
                v-for="(selector) in selectorTabs"
                :key="selector.type"
                :class="['ip-tab-radio', { 'disabled': !editable }]"
                @click="onChooseSelector(selector.id)">
                <span :class="['radio', { 'checked': activeSelector === selector.id }]"></span>
                <span class="radio-text">{{selector.name}}</span>
            </div>
        </div>
        <div class="selector-content">
            <static-ip
                v-show="activeSelector === 'ip'"
                ref="ip"
                :allow-unfold-input="allowUnfoldInput"
                :editable="editable"
                :static-ip-list="staticIpList"
                :static-ips="staticIps"
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
            staticIps: Array,
            dynamicIps: Array,
            dynamicGroups: Array,
            manualInput: Object
        },
        data () {
            return {
                activeSelector: this.selectors[0]
            }
        },
        watch: {
            selectors (val, oldVal) {
                if (val.toString() !== oldVal.toString()) {
                    this.activeSelector = val[0]
                }
            }
        },
        methods: {
            onChooseSelector (id) {
                if (!this.editable) {
                    return
                }
                this.$emit('change', 'selectors', [id])
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
    min-width: 120px;
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
</style>
