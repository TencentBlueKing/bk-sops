/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="select-list">
        <template>
            <van-cell
                is-link
                arrow-direction="down"
                :title="label"
                :value="value"
                @click="show = true">
                {{ value }}
            </van-cell>
        </template>
        <van-popup
            v-model="show"
            position="bottom"
            :overlay="true">
            <van-cell-group>
                <template v-if="multiple">
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
                </template>
                <tempate v-else>
                    <van-picker
                        show-toolbar
                        :columns="multipleSelectOptions"
                        :default-index="defaultIndex"
                        @confirm="onConfirm"
                        @cancel="show = false" />
                </tempate>
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
            },
            data: {
                type: Object,
                default () {
                    return {}
                }
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
                defaultIndex: {
                    type: Number,
                    default: 0
                },
                choseKey: {
                    type: String,
                    default: ''
                },
                multipleSelectOptions: [],
                show: false
            }
        },
        created () {
            this.multiple = this.select.multiple
            if (this.multiple) {
                this.defaultVal = this.select.defaultVal
                this.select.columns.forEach(item => {
                    item.selected = this.defaultVal.includes(item.value)
                })
                this.multipleSelectOptions = this.select.columns
                this.checkedValue = this.data.value
            } else {
                this.multipleSelectOptions = this.select.columns.map(item => {
                    return { text: item.text || item.name, key: item.value }
                })
                this.defaultIndex = this.select.defaultIndex
                if (this.defaultIndex === -1) {
                    this.defaultIndex = 0
                }
                this.value = this.multipleSelectOptions[this.defaultIndex].text
                this.choseKey = this.multipleSelectOptions[this.defaultIndex].key
            }
        },
        methods: {
            onOptionClick (option) {
                this.$set(option, 'selected', !option.selected)
                this.value = this.multipleSelectOptions.filter(o => o.selected).map(o => o.text).join(',')
                this.checkedValue = this.multipleSelectOptions.filter(o => o.selected).map(o => o.value).join(',')
            },
            onConfirm (option) {
                this.show = false
                this.value = option.text
                this.choseKey = option.key
            }
        }
    }
</script>
