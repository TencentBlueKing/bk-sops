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
    <div class="multiple-ip-selector">
        <div class="selector-choose-wrap">
            <div
                v-for="selector in selectorTabs"
                :key="selector.type"
                :class="['ip-tab-checkbox', { 'disabled': !editable }]"
                @click="onChooseSelector(selector.id)">
                <span :class="['checkbox', { 'checked': selectors.indexOf(selector.id) > -1 }]"></span>
                <span class="checkbox-text">{{selector.name}}</span>
            </div>
        </div>
        <div class="tab-nav-container">
            <div class="tab-list">
                <template v-for="selector in selectorTabs">
                    <div
                        v-if="selectors.indexOf(selector.id) > -1"
                        :key="selector.type"
                        :class="['tab-item', { 'tab-item-active': activeSelector === selector.id }]"
                        :editable="editable"
                        @click="onChangeTab(selector.id)">
                        {{selector.name}}
                    </div>
                </template>
            </div>
        </div>
        <div class="selector-content">
            <static-ip
                v-show="activeSelector === 'ip'"
                ref="ip"
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
        </div>
    </div>
</template>
<script>
    import StaticIp from './StaticIp.vue'
    import DynamicIp from './DynamicIp.vue'

    export default {
        name: 'MultipleIpSelector',
        components: {
            StaticIp,
            DynamicIp
        },
        props: ['editable', 'selectorTabs', 'selectors', 'staticIpList', 'dynamicIpList', 'dynamicIps', 'staticIps'],
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
                const selectors = this.selectors.slice(0)
                const index = selectors.indexOf(id)
                if (index > -1) {
                    if (selectors.length === 1) {
                        return
                    }
                    selectors.splice(index, 1)
                    if (id === this.activeSelector) {
                        this.activeSelector = selectors[0]
                    }
                } else {
                    selectors.push(id)
                }
                this.$emit('change', 'selectors', selectors)
            },
            onChangeTab (id) {
                this.activeSelector = id
            },
            onStaticIpChange (val) {
                this.$emit('change', 'ip', val)
            },
            onDynamicIpChange (val) {
                this.$emit('change', 'topo', val)
            },
            validate () {
                let isValidate = true
                this.selectors.forEach(item => {
                    const result = this.$refs[item].validate()
                    if (!result) {
                        // this.onChangeTab(item)
                        isValidate = false
                    }
                })
                return isValidate
            }
        }
    }
</script>
<style lang="scss" scoped>
.selector-choose-wrap {
    margin-bottom: 20px;
}
.ip-tab-checkbox {
    display: inline-block;
    margin-right: 30px;
    font-size: 14px;
    vertical-align: middle;
    cursor: pointer;
    .checkbox {
        display: inline-block;
        position: relative;
        width: 14px;
        height: 14px;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        vertical-align: middle;
        &.checked {
            background: #3a84ff;
            border-color: #3a84ff;
            &:before {
                content: "";
                position: absolute;
                left: 2px;
                top: 2px;
                height: 4px;
                width: 8px;
                border-left: 1px solid;
                border-bottom: 1px solid;
                border-color: #ffffff;
                transform: rotate(-45deg);
            }
        }
    }
    &.disabled {
        color: #cccccc;
        cursor: not-allowed;
        .checkbox {
            background: #cccccc;
            border-color: #cccccc;
        }
    }
}

.tab-nav-container {
    border-bottom: 1px solid #dcdee5;
}
.tab-list {
    display: inline-block;
    margin-bottom: -1px;
    font-size: 0;
    background: #fff;
    .tab-item {
        display: inline-block;
        margin: 0;
        padding: 10px;
        width: 96px;
        line-height: 20px;
        font-size: 14px;
        border: 1px solid #dcdee5;
        border-right: none;
        text-align: center;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
        }
        &:first-child {
            border-top-left-radius: 2px;
        }
        &:last-child {
            border-right: 1px solid #dcdee5;
            border-top-right-radius: 2px;
        }
    }
    .tab-item-active {
        color: #3a84ff;
        border-bottom: none;
    }
}
</style>
