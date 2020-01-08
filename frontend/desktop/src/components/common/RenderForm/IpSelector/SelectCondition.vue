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
    <div class="ip-select-conditon">
        <h3 :class="['condition-label', { 'disabled': !editable }]">{{label}}{{i18n.allSatisfy}}:</h3>
        <template v-if="conditions.length" class="condition-list">
            <div
                v-for="(condition, index) in conditions"
                :key="index"
                class="condition-content">
                <condition-item
                    :ref="`conditionItem_${index}`"
                    :data="condition"
                    :fields-list="conditionFields"
                    :index="index"
                    :editable="editable"
                    @changeCondition="changeCondition"
                    @addCondition="addCondition(index)"
                    @deleteCondition="deleteCondition(index)">
                </condition-item>
            </div>
        </template>
        <div v-else :class="['condition-empty', { 'disabled': !editable }]" @click.stop="addCondition">{{i18n.addItem + label}}</div>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import ConditionItem from './ConditionItem.vue'

    const i18n = {
        allSatisfy: gettext('（同时满足）'),
        addItem: gettext('增加一条')
    }

    export default {
        name: 'SelectCondition',
        components: {
            ConditionItem
        },
        props: ['editable', 'label', 'conditions', 'conditionFields'],
        data () {
            return {
                i18n
            }
        },
        methods: {
            changeCondition (data, index) {
                const conditions = this.conditions.slice(0)
                conditions.splice(index, 1, data)
                this.$emit('change', conditions)
            },
            addCondition (index = 0) {
                if (!this.editable) {
                    return
                }
                const conditions = this.conditions.slice(0)
                conditions.splice(index + 1, 0, {
                    field: '',
                    value: []
                })
                this.$emit('change', conditions)
            },
            deleteCondition (index) {
                const conditions = this.conditions.slice(0)
                conditions.splice(index, 1)
                this.$emit('change', conditions)
            },
            validate () {
                let isValid = true
                if (this.conditions.length) {
                    this.conditions.forEach((item, index) => {
                        const condition = `conditionItem_${index}`
                        const result = this.$refs[condition][0].validate()
                        if (!result) {
                            isValid = false
                        }
                    })
                }
                return isValid
            }
        }
    }
</script>
<style lang="scss" scoped>
.condition-label {
    margin: 18px 0;
    line-height: 20px;
    color: #313138;
    font-size: 14px;
    font-weight: 400;
    &.disabled {
        color: #cccccc;
    }
}
.condition-empty {
    padding: 21px;
    line-height: 20px;
    color: #c4c6cc;
    font-size: 14px;
    text-align: center;
    border: 1px dotted #c4c6cc;
    &:not(.disabled) {
        cursor: pointer;
        &:hover {
            color: #3a84ff;
            border-color: #3a84ff;
        }
    }
}
</style>
