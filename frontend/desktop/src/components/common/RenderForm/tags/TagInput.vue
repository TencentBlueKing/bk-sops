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
    <div class="tag-input">
        <div v-if="formMode">
            <div class="rf-form-wrapper">
                <el-input
                    type="text"
                    v-model="inputValue"
                    :disabled="!editable"
                    :placeholder="placeholder"
                    @input="onInput">
                </el-input>
                <transition>
                    <div class="rf-select-list" v-show="showVarList && isListOpen">
                        <ul class="rf-select-content">
                            <li
                                class="rf-select-item"
                                v-for="item in varList"
                                :key="item"
                                @click.stop="onSelectVal(item)">
                                {{item}}
                            </li>
                        </ul>
                    </div>
                </transition>
            </div>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{(value === 'undefined' || value === '') ? '--' : value}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    import dom from '@/utils/dom.js'
    import { getFormMixins } from '../formMixins.js'

    const VAR_REG = /\$\{\w*$/

    const inputAttrs = {
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        },
        value: {
            type: String,
            required: false,
            default: ''
        },
        showVarList: {
            type: Boolean,
            default: false
        }
    }
    export default {
        name: 'TagInput',
        mixins: [getFormMixins(inputAttrs)],
        data () {
            return {
                isListOpen: false,
                varList: []
            }
        },
        computed: {
            ...mapState({
                'constants': state => state.template.constants
            }),
            constantArr: {
                get () {
                    if (this.constants) {
                        return Object.keys(this.constants)
                    }
                    return []
                },
                set (val) {
                    this.varList = val
                }
            },

            inputValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.updateForm(val)
                }
            }
        },
        created () {
            window.addEventListener('click', this.handleListShow, false)
        },
        before () {
            window.removeEventListener('click', this.handleListShow, false)
        },
        methods: {
            handleListShow (e) {
                if (!this.isListOpen) {
                    return
                }
                const listPanel = document.querySelector('.rf-select-list')
                if (listPanel && !dom.nodeContains(listPanel, e.target)) {
                    this.isListOpen = false
                }
            },
            onInput (val) {
                const matchResult = val.match(VAR_REG)
                if (matchResult && matchResult[0]) {
                    const regStr = matchResult[0].replace(/[\$\{\}]/g, '\\$&')
                    const inputReg = new RegExp(regStr)
                    this.varList = this.constantArr.filter(item => {
                        return inputReg.test(item)
                    })
                } else {
                    this.varList = []
                }
                this.isListOpen = !!this.varList.length
            },
            onSelectVal (val) {
                const replacedValue = this.value.replace(VAR_REG, val)
                this.updateForm(replacedValue)
                this.isListOpen = false
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';

.tag-input {
    /deep/ .el-input__inner {
        height: 36px;
        line-height: 36px;
        padding: 0 10px;
    }
    .rf-form-wrapper {
        position: relative;
        .rf-select-list {
            position: absolute;
            top: 40px;
            right: 0;
            width: 100%;
            background: #ffffff;
            border-radius: 2px;
            box-shadow: 0 0 8px 1px rgba(0, 0, 0, 0.1);
            overflow-y: hidden;
            z-index: 100;
        }
        .rf-select-content {
            max-height: 100px;
            overflow: auto;
            @include scrollbar;
        }
        .rf-select-item {
            padding: 0 10px;
            line-height: 32px;
            font-size: 14px;
            cursor: pointer;
            &:hover {
                background: #eef6fe;
                color: #3c96ff;
            }
        }
    }
}
</style>
