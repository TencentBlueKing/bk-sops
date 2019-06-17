/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="select-list">
        <template v-if="multiple">
            <van-cell
                is-link
                arrow-direction="down"
                :title="label"
                :value="value"
                @click="show = true">
                {{ value }}
            </van-cell>
        </template>
        <template v-else>
            <van-cell
                :title="label"
                :value="data.value">
                {{ data.value }}
            </van-cell>
        </template>
        <van-popup
            v-model="show"
            position="bottom"
            :overlay="true">
            <van-cell-group>
                <van-cell
                    v-for="option in multipleSelectOptions"
                    :key="option.value"
                    center="true"
                    :title="option.text"
                    clickable
                    @click="onOptionClick(option)">
                    <van-icon
                        slot="right-icon"
                        name="success"
                        v-show="option.selected"
                        color="#1989FA" />
                </van-cell>
            </van-cell-group>
        </van-popup>
    </div>
</template>

<script>
    export default {
        name: 'VantSelect',
        props: {
            label: {
                type: String,
                default: ''
            },
            placeholder: {
                type: String,
                default: ''
            },
            value: {
                type: String,
                default: ''
            },
            select: {
                type: Object
            }
        },
        data () {
            return {
                multiple: {
                    type: Boolean,
                    default: false
                },
                defaultVal: {
                    type: Array,
                    default: []
                },
                multipleSelectOptions: [],
                show: false
            }
        },
        created () {
            this.multiple = this.select.multiple
            this.defaultVal = this.select.defaultVal
            if (this.multiple) {
                this.select.columns.forEach(item => {
                    item.selected = this.defaultVal.includes(item.value)
                })
                this.multipleSelectOptions = this.select.columns
            }
        },
        methods: {
            onOptionClick (option) {
                this.$set(option, 'selected', !option.selected)
                this.value = this.multipleSelectOptions.filter(o => o.selected).map(o => o.text).join(',')
            }
        }
    }
</script>
