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
    <input
        type="text"
        class="base-input"
        ref="baseInput"
        :title="title"
        :value="value"
        :name="name"
        @input="onInput"
        @blur="onBlur"
        @keyup.enter="onKeyupEnter">
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'BaseInput',
    model: {
        prop: 'value',
        event: 'input'
    },
    props: ['value', 'name','title'],
    methods: {
        focus () {
            this.$refs.baseInput.focus()
        },
        select () {
            this.$refs.baseInput.select()
        },
        onInput (e) {
            this.$emit('input', e.target.value)
        },
        onBlur (e) {
            this.$emit('blur', e.target.value)
        },
        onKeyupEnter (e) {
            this.$emit('enter', e.target.value)
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.base-input {
    display: inline-block;
    padding: 0 10px;
    width: 100%;
    height: 36px;
    line-height: 36px;
    color: #606266;
    font-size: 14px;
    background: #fff;
    border: 1px solid $commonBorderColor;
    border-radius: 4px;
    outline: 0;
    &:hover {
        border-color: #c0c4cc;
    }
    &:focus {
        border-color: #3c96ff;
    }
    &.disabled {
        color: #aaa;
        background: #fafafa;
        cursor: not-allowed;
    }
}
</style>


