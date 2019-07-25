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
    <div class="advanced-search">
        <span class="search-content" @click="onShow">
            {{i18n.advancedSearch}}
            <div class="advanced-shape">
                <i class="bk-icon icon-down-shape search-shape" v-if="!shapeShow"></i>
                <i class="bk-icon icon-up-shape search-up-shape" v-if="shapeShow"></i>
            </div>
        </span>
        <bk-input
            class="search-input"
            v-model="localValue"
            :clearable="true"
            :placeholder="inputPlaceholader"
            :right-icon="'bk-icon icon-search'"
            @change="onInput"></bk-input>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    export default {
        name: 'BaseSearch',
        props: ['inputPlaceholader', 'value'],
        data () {
            return {
                i18n: {
                    advancedSearch: gettext('高级搜索')
                },
                isAdvancedSerachShow: false,
                shapeShow: false,
                localValue: ''
            }
        },
        watch: {
            value: {
                handler (value) {
                    this.localValue = value
                },
                deep: true
            }
        },
        methods: {
            onShow () {
                this.$emit('onShow', this.isAdvancedSerachShow)
                this.shapeShow = !this.shapeShow
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
    margin: 20px;
    .search-input {
        display: inline-block;
        width: 360px;
    }
    .search-input.placeholder {
        color: $formBorderColor;
      }
    }
    .search-content {
        margin: 30px;
        color:#313238;
        font-size: 14px;
        font-weight: 400;
        cursor: pointer;
        &:hover {
            color: #3c96ff;
        }
        .advanced-shape {
            display: inline-block;
            margin-left: 5px;
            font-size: 12px;
            color:#cccccc;
            &:hover {
                color: #3c96ff;
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
