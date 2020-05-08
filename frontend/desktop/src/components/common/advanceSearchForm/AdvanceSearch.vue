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
    <div class="advanced-search">
        <div class="search-content">
            <div :class="['toggle-open-btn', { opened: isAdvanceOpen }]" @click="onShow">
                <span>{{i18n.advancedSearch}}</span>
                <span class="advanced-shape">
                    <i class="bk-icon icon-down-shape search-shape" v-if="!isAdvanceOpen"></i>
                    <i class="bk-icon icon-up-shape search-up-shape" v-else></i>
                </span>
            </div>
            <slot name="extend"></slot>
        </div>
        <bk-input
            class="search-input"
            v-model="localValue"
            :clearable="true"
            :placeholder="inputPlaceholader"
            :right-icon="'bk-icon icon-search'"
            @change="onInput">
        </bk-input>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    export default {
        name: 'AdvanceSearch',
        props: {
            inputPlaceholader: {
                type: String,
                default: ''
            },
            isAdvanceOpen: {
                type: Boolean,
                default: false
            },
            value: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                i18n: {
                    advancedSearch: gettext('高级搜索')
                },
                isAdvancedSerachShow: false,
                localValue: this.value
            }
        },
        watch: {
            value (value) {
                this.localValue = value
            }
        },
        methods: {
            onShow () {
                this.$emit('update:isAdvanceOpen', !this.isAdvanceOpen)
            },
            onInput (value) {
                const exportValue = typeof value === 'string' ? value : value.target.value
                this.$emit('input', exportValue)
            }
        }
    }
</script>

<style lang='scss'>
@import '@/scss/config.scss';
.advanced-search {
    position: relative;
    float: right;
    display: flex;
    align-items: center;
    .search-input {
        display: inline-block;
        width: 360px;
    }
    .search-input.placeholder {
        color: $formBorderColor;
      }
    }
    .search-content {
        margin: 0 30px;
        color:#313238;
        font-size: 14px;
        font-weight: 400;
        .toggle-open-btn {
            display: inline-block;
            cursor: pointer;
            &.opened,
            &:hover {
                color: #3a84ff;
                .advanced-shape {
                    color: #3a84ff;
                }
            }
            .advanced-shape {
                display: inline-block;
                margin-left: 5px;
                font-size: 12px;
                color:#cccccc;
            }
        }
    }

.common-icon-search {
    position: absolute;
    right: 15px;
    top: 8px;
    color: #63656e;
}
</style>
