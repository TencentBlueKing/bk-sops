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
    <div class="condition-item">
        <div class="select-field">
            <bk-selector
                :placeholder="i18n.select"
                :disabled="!editable"
                :selected.sync="condition.field"
                :list="filedsData"
                @item-selected="onConditionSelect">
            </bk-selector>
            <span v-show="filedError" class="common-error-tip error-info">{{i18n.notEmpty}}</span>
        </div>
        <div class="condition-text-wrap">
            <pre class="textarea-mirror"><span>{{condition.value}}</span><br><br></pre>
            <textarea
                :placeholder="i18n.desc"
                v-model="condition.value"
                :class="{'disabled': !editable}"
                :disabled="!editable"
                @change="onConditionTextChange">
            </textarea>
            <span v-show="valueError" class="common-error-tip value-error">{{i18n.notEmpty}}</span>
        </div>
        <div class="operation-wrap">
            <i :class="['operation-btn', 'add-condition', {'disabled': !editable}]" @click.stop="onAddCondition"></i>
            <i :class="['operation-btn', 'delete-condition', {'disabled': !editable}]" @click.stop="onDeleteCondition"></i>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

const i18n = {
    select: gettext('请选择'),
    desc: gettext('输入筛选条件，多条筛选条件换行隔开'),
    notEmpty: gettext('必填项')
}

export default {
    name: 'ConditionItem',
    props: ['editable', 'data', 'fieldsList', 'index'],
    data () {
        return {
            isDropdownShow: false,
            filedError: false,
            valueError: false,
            condition: {
                field: this.data.field,
                value: this.data.value.join('\n')
            },
            i18n
        }
    },
    computed: {
        filedsData () {
            return this.fieldsList.map(item => {
                return {
                    id: item.bk_obj_id,
                    name: item.bk_obj_name
                }
            })
        }
    },
    watch: {
        data: {
            handler (val) {
                this.condition = {
                    field: val.field,
                    value: val.value.join('\n')
                }
            },
            deep: true
        }
    },
    methods: {
        onConditionSelect (value) {
            const condition = {
                field: value,
                value: this.data.value
            }
            this.$emit('changeCondition', condition, this.index)
        },
        onConditionTextChange () {
            const condition = {
                field: this.condition.field,
                value: this.condition.value.split('\n')
            }
            this.$emit('changeCondition', condition, this.index)
        },
        onAddCondition () {
            if (!this.editable) {
                return
            }
            this.$emit('addCondition')
        },
        onDeleteCondition (data) {
            if (!this.editable) {
                return
            }
            this.$emit('deleteCondition')
        },
        validate () {
            this.filedError = !this.condition.field
            this.valueError = !this.condition.value
            return !this.filedError && !this.valueError
        }
    }
}
</script>
<style lang="scss" scoped>
.condition-item {
    margin-bottom: 20px;
    &::after {
        display: block;
        content: "";
        clear: both;
    }
}
    
.select-field {
    float: left;
    width: 120px;
}
.condition-text-wrap {
    float: left;
    position: relative;
    margin: 0 10px;
    width: calc(100% - 120px - 20px - 60px);
    .textarea-mirror, textarea {
        padding: 9px 10px 0;
        line-height: 1.2;
        width: 100%;
        font-size: 14px;
        border: 1px solid #c3cdd7;
        border-radius: 2px;
    }
    .textarea-mirror {
        margin: 0;
        min-height: 58px;
        max-height: 400px;
        font-size: 14px;
        line-height: 1.2;
        white-space: pre-wrap;
        word-wrap: break-word;
        opacity: 0;
        visibility: hidden;
    }
    textarea {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        resize: none;
        outline: none;
        &.disabled {
            color: #aaaaaa;
            background: #fafafa;
            cursor: not-allowed;
        }
        &:focus {
            border-color: #3a84ff;
        }
        &::-webkit-input-placeholder {
            color: #c3cdd7;
        }
        &::-webkit-scrollbar {
            width: 4px;
            height: 4px;
            &-thumb {
                border-radius: 20px;
                background: #a5a5a5;
                box-shadow: inset 0 0 6px hsla(0,0%,80%,.3);
            }
        }
    }
    .value-error {
        position: absolute;
        bottom: -16px;
        left: 0;
    }
}
.operation-wrap {
    float: right;
    margin-top: 10px;
    text-align: right;
    user-select: none;
    .operation-btn {
        display: inline-block;
        position: relative;
        margin-right: 6px;
        width: 17px;
        height: 17px;
        background: #989dab;
        border-radius: 50%;
        cursor: pointer;
        &:not(.disabled):hover {
            background: #3a84ff;
        }
        &:last-child {
            margin-right: 0;
        }
        &.disabled {
            cursor: not-allowed;
        }
    }
    .add-condition {
        &:before {
            content: '';
            position: absolute;
            top: 8px;
            left: 4px;
            width: 9px;
            height: 1px;
            background: #ffffff;
        }
        &:after {
            content: '';
            position: absolute;
            top: 4px;
            left: 8px;
            width: 1px;
            height: 9px;
            background: #ffffff;
        }
    }
    .delete-condition:before {
        content: '';
        position: absolute;
        top: 8px;
        left: 4px;
        width: 9px;
        height: 1px;
        background: #ffffff;
    }
}
</style>




