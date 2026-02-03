/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-select">
        <div v-if="formMode">
            <el-select
                ref="selectComp"
                v-model="seletedValue"
                v-loading="loading"
                v-markTag="{ multiple, hasGroup, seletedValue, options: items }"
                filterable
                default-first-option
                :clearable="clearable"
                popper-class="tag-component-popper"
                :allow-create="allowCreate"
                :disabled="!editable || disabled"
                :remote="remote"
                :multiple-limit="multiple_limit"
                :multiple="multiple"
                :no-data-text="empty_text"
                :filter-method="filterMethod"
                :placeholder="placeholder"
                @visible-change="onVisibleChange">
                <template v-if="showRightBtn" slot="prefix">
                    <i class="right-btn" :class="rightBtnIcon" @click="onRightBtnClick"></i>
                </template>
                <template v-if="!hasGroup">
                    <el-option
                        v-for="item in options"
                        :key="item.value"
                        :label="item.text"
                        :value="item.value">
                        <span class="option-item">{{ item.text }}</span>
                    </el-option>
                </template>
                <template v-else>
                    <el-option-group
                        v-for="group in options"
                        :key="group.value"
                        :label="group.text">
                        <el-option
                            v-for="item in group.options"
                            :key="item.value"
                            :label="item.text"
                            :value="item.value">
                            <span class="option-item">{{ item.text }}</span>
                        </el-option>
                    </el-option-group>
                </template>
            </el-select>
            <p v-if="multiple" class="selected-tip">
                {{ $t('已选') }}
                <span class="count">{{ seletedValue.length }}</span>
                {{ $t('项') }}
                <bk-button
                    class="ml10"
                    :disabled="!editable || disabled || !seletedValue.length"
                    text
                    title="primary"
                    @click="onClear">
                    {{ $t('清除') }}
                </bk-button>
            </p>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{ viewValue || '--' }}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
    import bus from '@/utils/bus.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        value: {
            type: [String, Array, Object, Boolean, Number],
            required: false,
            default: '',
            desc: i18n.t('下拉框的选中值，可输入 String、Boolean、Number 类型的值，若为多选请输入包含上述类型的数组格式数据')
        },
        items: {
            type: Array,
            required: false,
            default () {
                return []
            },
            desc: "array like [{text: '', value: ''}, {text: '', value: ''}]"
        },
        multiple: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'set multiple selected items'
        },
        multiple_limit: {
            type: Number,
            required: false,
            default: 0,
            desc: 'limit of selected items when multiple is true'
        },
        clearable: {
            type: Boolean,
            required: false,
            default: true,
            desc: 'show the icon for clearing input value'
        },
        allowCreate: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'create value in input field'
        },
        remote: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'use remote data or not'
        },
        remote_url: {
            type: [String, Function],
            required: false,
            default: '',
            desc: 'remote url when remote is true'
        },
        remote_data_init: {
            type: Function,
            required: false,
            default: function (data) {
                return data
            },
            desc: 'how to process data after getting remote data'
        },
        hasGroup: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'whether the options in group'
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'selector is disabled'
        },
        placeholder: {
            type: String,
            required: false,
            default: '',
            desc: 'placeholder'
        },
        showRightBtn: {
            type: Boolean,
            required: false,
            default: false,
            desc: 'whether to display the button on the right of the selection box'
        },
        rightBtnIcon: {
            type: String,
            required: false,
            default: 'common-icon-box-top-right-corner',
            desc: 'button icon to the right of the selection box'
        },
        rightBtnCb: {
            type: Function,
            required: false,
            default: null,
            desc: 'Button to the right of the selection box to click on the event callback function'
        },
        empty_text: {
            type: String,
            required: false,
            default: i18n.t('无数据'),
            desc: 'tips when data is empty'
        }
    }
    export default {
        name: 'TagSelect',
        directives: {
            // 对于多选输入框，用户输入的选项做一个标记
            markTag: {
                componentUpdated (el, binding, vnode) {
                    const { hasGroup, multiple, options, seletedValue } = binding.value
                    if (multiple) {
                        const vm = vnode.context
                        const indexs = []
                        seletedValue.forEach((val, index) => {
                            let valInOptions = false
                            if (hasGroup) {
                                valInOptions = options.some(group => {
                                    return group.options.some(item => {
                                        if (item.value === val) {
                                            return true
                                        }
                                    })
                                })
                            } else {
                                valInOptions = options.some(item => {
                                    if (item.value === val) {
                                        return true
                                    }
                                })
                            }
                            if (!valInOptions) {
                                indexs.push(index)
                            }
                        })
                        // 需要在输入框子流程dom更新之后才能操作
                        vm.$nextTick(() => {
                            setTimeout(() => {
                                const $tagEls = el.querySelectorAll('.el-select__tags .el-tag')
                                $tagEls.forEach((tagEl, i) => {
                                    if (indexs.includes(i)) {
                                        tagEl.classList.add('individual')
                                    } else {
                                        tagEl.classList.remove('individual')
                                    }
                                })
                            }, 0)
                        })
                    }
                }
            }
        },
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                options: this.$attrs.items ? this.$attrs.items.slice(0) : [],
                loading: false,
                loading_text: this.$t('加载中'),
                selectInputDom: null,
                searchQuery: '', // 搜索关键词
                isRestoring: false // 是否正在恢复搜索状态
            }
        },
        computed: {
            seletedValue: {
                get () {
                    return this.value
                },
                set (val) {
                    if (!this.hook) {
                        this.updateForm(val)
                        // 多选模式下，选中后恢复搜索关键词
                        if (this.multiple && this.searchQuery) {
                            this.isRestoring = true
                            this.$nextTick(() => {
                                const selectComp = this.$refs.selectComp
                                if (selectComp) {
                                    selectComp.query = this.searchQuery
                                    const inputVal = this.searchQuery.split(',')
                                    this.options = this.items.filter(option => inputVal.some(i => option.text.toLowerCase().includes(i.toLowerCase())))
                                }
                                this.isRestoring = false
                            })
                        }
                    }
                }
            },
            viewValue () {
                if (Object.prototype.toString.call(this.value) === '[object object]') {
                    return this.value
                }
                if (Array.isArray(this.seletedValue)) { // 多选
                    if (!this.seletedValue.length) {
                        return '--'
                    }
                    if (this.items.length) {
                        return this.seletedValue.map(val => {
                            return this.filterLabel(val)
                        }).join(',')
                    } else {
                        return this.value.join(',')
                    }
                } else { // 单选
                    if (this.seletedValue === 'undefined') {
                        return '--'
                    }
                    if (this.items.length) {
                        return this.filterLabel(this.seletedValue)
                    } else {
                        return this.value
                    }
                }
            }
        },
        watch: {
            items (val) {
                this.options = val.slice(0)
            }
        },
        mounted () {
            this.remoteMethod()
            if (this.multiple) {
                this.selectInputDom = this.$el.querySelector('.el-select .el-select__input')
                if (!this.selectInputDom) return
                this.selectInputDom.addEventListener('paste', this.handleSelectPaste)
            }
        },
        beforeDestroy () {
            if (this.selectInputDom) {
                this.selectInputDom.removeEventListener('paste', this.handleSelectPaste)
            }
        },
        methods: {
            filterLabel (val) {
                let label = val
                this.items.some(item => {
                    if (item.value === val) {
                        label = item.text
                        return true
                    }
                })
                return label
            },
            // 自定义搜索，支持以','符号分隔的多条数据搜索
            filterMethod (val) {
                // 避免被组件自动调用清空
                if (!this.isRestoring) {
                    this.searchQuery = val
                }
                
                if (!val) {
                    this.options = this.items.slice(0)
                    return
                }

                const inputVal = val.split(',')
                this.options = this.items.filter(option => inputVal.some(i => option.text.toLowerCase().includes(i.toLowerCase())))
            },
            set_loading (loading) {
                this.loading = loading
            },
            remoteMethod () {
                const self = this
                const remote_url = typeof this.remote_url === 'function' ? this.remote_url() : this.remote_url
                if (!remote_url) return

                // 请求远程数据
                this.loading = true
                $.ajax({
                    url: remote_url,
                    method: 'GET',
                    xhrFields: {
                        withCredentials: true
                    },
                    success: function (res) {
                        const data = self.remote_data_init(res) || []

                        self.items = data
                        self.loading = false
                        // 远程数据源模式下，下拉框变量需携带json数据
                        const remoteData = JSON.stringify(data)
                        bus.$emit('tagRemoteLoaded', self.tagCode, remoteData)
                    },
                    error: function (resp) {
                        self.placeholder = self.$t('请求数据失败')
                        self.loading = false
                    }
                })
            },
            onRightBtnClick () {
                typeof this.rightBtnCb === 'function' && this.rightBtnCb()
            },
            onVisibleChange (val) {
                if (!val) { // 下拉框隐藏后，还原搜索过滤掉的选项
                    this.options = this.items.slice(0)
                    this.searchQuery = ''
                }
            },
            onClear () {
                this.updateForm([])
            },
            handleSelectPaste (event) {
                let paste = (event.clipboardData || window.clipboardData).getData('text')
                paste = paste.replace(/\\(t|s)/g, ' ')
                const selection = window.getSelection()
                if (!selection.rangeCount) return false
                paste = paste.split(/,|;|\s+/).filter(item => item)
                if (paste.length > 1) { // 粘贴多个时才禁用默认行为
                    event.preventDefault()
                }
                const matchVal = []
                // 粘贴时先判断是否完全匹配，再忽略大小写匹配
                const texts = this.items.map(option => option.text)
                paste.forEach(item => {
                    const iaMatch = texts.includes(item)
                    const option = this.items.find(option => {
                        return iaMatch ? option.text === item : item.toLowerCase() === option.text.toLowerCase()
                    })
                    if (option) {
                        matchVal.push(option.value)
                    }
                })
                // 单个场景，完全匹配的直接填上，否则执行搜索逻辑
                if (paste.length === 1 && matchVal.length === 0) {
                    return
                }
                if (this.multiple) {
                    const setArr = [...this.value, ...matchVal]
                    this.updateForm([...new Set(setArr)])
                }
                this.$refs.selectComp.blur()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .el-select {
        position: relative;
        width: 100%;
        ::v-deep .el-input__inner {
            padding-left: 10px;
            padding-right: 60px;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
        }
        ::v-deep .el-input__prefix {
            left: auto;
            right: 28px;
        }
        ::v-deep .el-tag.el-tag--info.el-tag--small.el-tag--light { // 解决已选多选项选项过长不换行问题
            height: auto;
            &.individual {
                background: rgba(254, 156, 0, 0.1);
            }
            .el-select__tags-text {
                white-space: normal;
                word-break: break-all;
                height: auto;
            }
        }
        .right-btn {
            display: flex;
            align-items: center;
            height: 100%;
            color: #63656e;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
    }
    .selected-tip {
        color: #979ba5;
        margin-top: 5px;
        .count {
            color: #313238;
        }
    }
</style>
<style lang="scss">
    .tag-component-popper {
        .el-select-dropdown {
            max-width: 500px;
            .el-select-dropdown__item { // 解决选项过长问题
                white-space: normal;
                word-break: break-all;
                height: auto;
            }
        }
    }
</style>
