/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="single-ip-selector">
        <div class="selector-choose-wrap">
            <div
                v-for="selector in selectorTabs"
                :key="selector.type"
                :class="['ip-tab-radio', {'disabled': !editable}]"
                @click="onChooseSelector(selector.id)">
                <span :class="['radio', {'checked': activeSelector === selector.id}]"></span>
                <span class="radio-text">{{selector.name}}</span>
            </div>
        </div>
        <div class="selector-content">
            <static-ip
                v-show="activeSelector === 'ip'"
                ref="ip"
                :editable="editable"
                :staticIpList="staticIpList"
                :staticIps="staticIps"
                @change="onStaticIpChange">
            </static-ip>
            <dynamic-ip
                v-show="activeSelector === 'topo'"
                ref="topo"
                :editable="editable"
                :dynamicIpList="dynamicIpList"
                :dynamicIps="dynamicIps"
                @change="onDynamicIpChange">
            </dynamic-ip>
        </div>
    </div>
</template>
<script>
import StaticIp from './StaticIp.vue'
import DynamicIp from './DynamicIp.vue'

export default {
    name: 'SingleIpSelector',
    components: {
        StaticIp,
        DynamicIp
    },
    props: ['editable', 'selectorTabs', 'selectors', 'staticIpList', 'dynamicIpList', 'staticIps', 'dynamicIps'],
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
        validate () {
            return this.$refs[this.activeSelector].validate()
        }
    }
}
</script>
<style lang="scss" scoped>
.selector-choose-wrap {
    margin-bottom: 20px;
}
.ip-tab-radio {
    display: inline-block;
    margin-right: 20px;
    font-size: 14px;
    cursor: pointer;
    .radio {
        display: inline-block;
        position: relative;
        width: 16px;
        height: 16px;
        border: 1px solid #c4c6cc;
        border-radius: 50%;
        vertical-align: middle;
        &.checked:before {
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


