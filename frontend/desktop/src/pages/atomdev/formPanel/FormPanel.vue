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
    <div class="form-panel">
        <draggable
            class="form-drag-area"
            filter=".operation-btn"
            :group="{ name: 'form', pull: true, put: 'tag' }"
            :list="formList"
            @add="onAddHander"
            @end="onSortHandler">
            <div class="form-item" v-for="(form, index) in formList" :key="index">
                <component
                    :is="form.tag === 'combine' ? 'Combine' : 'FormItem'"
                    :tag-info="tagInfo"
                    :form="form"
                    :index="index"
                    @combineAdded="combineAdded"
                    @onShowInfoClick="onShowInfoClick"
                    @onEditClick="onEditClick"
                    @onDeleteClick="onDeleteClick">
                </component>
                <!-- <div :class="['content-wrapper', { active: tagInfo && tagInfo.tagCode === form.config.tag_code }]">
                    <label class="form-item-label">{{ form.tag && form.config.attrs.name.value }}</label>
                    <div class="form-item-content">
                        <template v-if="form.tag">
                            <component :is="form.tag" v-bind="getFormProps(form.config)"></component>
                        </template>
                    </div>
                    <div class="content-mask">
                        <i class="operation-btn common-icon-horizon-line-group"></i>
                        <i
                            :class="[
                                'operation-btn',
                                'common-icon-tooltips',
                                { 'active': tagInfo && tagInfo.tagCode === form.config.tag_code }
                            ]"
                            @click="onShowInfoClick(form)">
                        </i>
                        <i class="operation-btn common-icon-box-pen" @click="onEditClick(form)"></i>
                        <i class="operation-btn bk-icon common-icon-close-linear-circle" @click="onDeleteClick(index)"></i>
                    </div>
                </div>
                <div v-if="tagInfo && tagInfo.tagCode === form.config.tag_code" class="tag-info">
                    <h3>{{tagInfo.title}}</h3>
                    <h3 v-if="tagInfo.desc">{{tagInfo.desc}}</h3>
                    <section v-if="tagInfo.attrs">
                        <p>{{ i18n.attr }}</p>
                        <template v-for="(attr, name) in tagInfo.attrs">
                            <p class="attr-item" :key="name">
                                {{name}}
                                <template v-if="attr.desc">：{{attr.desc}}</template>
                            </p>
                        </template>
                    </section>
                </div> -->
            </div>
        </draggable>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import draggable from 'vuedraggable'
    import tools from '@/utils/tools.js'
    import importTag from '../importTag.js'
    import FormItem from './FormItem.vue'
    import Combine from './Combine.vue'
    const { components: TAGS, attrs: ATTRS } = importTag()

    export default {
        name: 'FormPanel',
        components: {
            draggable,
            FormItem,
            Combine
        },
        props: {
            forms: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                formList: tools.deepClone(this.forms),
                tagInfo: null
            }
        },
        watch: {
            forms (val) {
                this.formList = tools.deepClone(val)
            }
        },
        methods: {
            getFormProps (config) {
                const formProps = {}
                Object.keys(config.attrs).reduce((acc, cur) => {
                    formProps[cur] = tools.deepClone(config.attrs[cur].value)
                }, formProps)
                return Object.assign(formProps, { tagCode: config.tag_code })
            },
            onAddHander () {
                const formListCopy = tools.deepClone(this.formList)
                this.$emit('updateForm', formListCopy)
            },
            onShowInfoClick (form) {
                if (this.tagInfo && this.tagInfo.tagCode === form.config.tag_code) {
                    this.tagInfo = null
                } else {
                    if (form.tag === 'combine') {
                        this.tagInfo = {
                            tagCode: form.config.tag_code,
                            title: form.tag,
                            attrs: {},
                            methods: {}
                        }
                    } else {
                        this.tagInfo = {
                            tagCode: form.config.tag_code,
                            title: form.tag,
                            attrs: ATTRS[form.tag],
                            methods: TAGS[form.tag].methods
                        }
                    }
                }
            },
            onEditClick (form) {
                this.$emit('editForm', form)
            },
            onDeleteClick (index) {
                const formListCopy = tools.deepClone(this.formList)
                formListCopy.splice(index, 1)
                this.$emit('updateForm', formListCopy)
            },
            onSortHandler (evt) {
                if (evt.newIndex !== evt.oldIndex) {
                    this.$emit('formSorted', tools.deepClone(this.formList))
                }
            },
            combineAdded (index, combineList) {
                this.formList[index] = combineList
                this.onAddHander()
            }
        }
    }
</script>
<style lang="scss">
    // 表单面板被拖动元素样式
    .form-drag-area {
        & > li.drag-entry,
        & > .sortable-ghost {
            position: relative;
            margin: 0 60px;
            height: 0;
            border-bottom: 2px solid #3a84ff;
            .content {
                display: none;
            }
            &:before {
                position: absolute;
                left: -6px;
                top: -3px;
                content: '';
                width: 4px;
                height: 4px;
                border: 2px solid #3a84ff;
                border-radius: 50%;
            }
        }
    }
</style>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';

    .form-panel {
        padding: 20px 10px;
        height: 100%;
        background: #e1e4e8;
        overflow-y: scroll;
        @include scrollbar;
    }
    .form-drag-area {
        min-height: 100%;
    }
    /deep/ {
        .rf-tag-hook {
            position: absolute;
            top: 4px;
            right: 0;
            z-index: 1;
        }
        .rf-view-value {
            display: inline-block;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
            word-wrap: break-word;
            word-break: break-all;
        }
        .el-table__empty-text{
            line-height: 20px;
            width: 100%;
        }
        .el-input__inner {
            height: 32px;
            line-height: 32px;
            font-size: 12px;
        }
        .el-radio__label,
        .el-checkbox__label {
            font-size: 12px;
            font-weight: normal;
            color: #63656e;
        }
        .el-tree-node__label,
        .el-tree__empty-block {
            font-size: 12px;
        }
        .el-select-dropdown .el-select-dropdown__item {
            font-size: 12px;
        }
        .tag-ip-selector {
            background: #ffffff;
        }
    }
    
</style>
