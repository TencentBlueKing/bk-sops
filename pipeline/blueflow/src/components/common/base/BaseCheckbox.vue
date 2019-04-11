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
    <div class="base-checkbox" @click.stop="onCheck">
        <span :class="['checkbox', {checked: this.checked}]">
        </span>
        <slot></slot>
    </div>
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'BaseCheckbox',
    props: ['isChecked'],
    data () {
        return {
            checked: this.isChecked || false
        }
    },
    methods: {
        onCheck () {
            this.checked = !this.checked
            this.$emit('checkCallback', this.checked)
        }
    },
    watch: {
        isChecked (val) {
            this.checked = val
        }
    }
}
</script>
<style lang="scss" scoped>
@import '../../../scss/config.scss';
.base-checkbox {
    display: inline-block;
    .checkbox {
        display: inline-block;
        position: relative;
        width: 14px;
        height: 14px;
        line-height: 14px;
        color: $whiteDefault;
        font-size: 12px;
        border: 1px solid $formBorderColor;
        border-radius: 2px;
        text-align: center;
        cursor: pointer;
        &:hover {
            border-color: $greyDark;
        }
        &.checked {
            background: $blueDefault;
            border-color: $blueDefault;
            &::after {
                content: "";
                position: absolute;
                left: 2px;
                top: 2px;
                height: 4px;
                width: 8px;
                border-left: 1px solid;
                border-bottom: 1px solid;
                border-color: $whiteDefault;
                transform: rotate(-45deg);
            }
        }
    }
}

</style>
