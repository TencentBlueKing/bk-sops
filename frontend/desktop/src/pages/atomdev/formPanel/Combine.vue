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
    <div class="combine-form">
        <div :class="['content-wrapper', { active: tagInfo && tagInfo.tagCode === form.config.tag_code }]">
            <!-- <label class="form-item-label">{{ form.tag && form.config.attrs.name.value }}</label> -->
            <div class="form-item-content">
                <draggable
                    class="form-drag-area form-drag-area-inner"
                    filter=".operation-btn"
                    :group="{ name: 'form', pull: true, put: ['tag', 'form'] }"
                    :list="formList"
                    @add="onAddHander"
                    @end="onSortHandler">
                    <component
                        v-for="(item, i) in formList"
                        :key="i"
                        :index="i"
                        :is="item.tag === 'combine' ? 'Combine' : 'FormItem'"
                        :tag-info="tagInfo"
                        :form="item"
                        @combineAdded="combineAdded"
                        @onShowInfoClick="onShowInfoClick"
                        @onEditClick="onEditClick"
                        @onDeleteClick="onDeleteClick">
                    </component>
                </draggable>
            </div>
            <div class="combine-move-icon">
                <i class="operation-btn common-icon-horizon-line-group"></i>
            </div>
            <div class="operation-btn-group">
                <i
                    :class="[
                        'operation-btn',
                        'common-icon-tooltips',
                        { 'active': tagInfo && tagInfo.tagCode === form.config.tag_code }
                    ]"
                    @click="$emit('onShowInfoClick',form)">
                </i>
                <i class="operation-btn common-icon-box-pen" @click="$emit('onEditClick', form)"></i>
                <i class="operation-btn bk-icon common-icon-close-linear-circle" @click="$emit('onDeleteClick', form.config.tag_code)"></i>
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
        </div>
    </div>
</template>

<script>
    import draggable from 'vuedraggable'
    import FormItem from './FormItem.vue'
    import tools from '@/utils/tools.js'

    export default {
        name: 'Combine',
        components: {
            draggable,
            FormItem
        },
        props: {
            tagInfo: {
                type: Object
            },
            form: {
                type: Object
            },
            index: {
                type: Number
            }
        },
        data () {
            return {
                i18n: {
                    attr: gettext('属性')
                },
                formList: tools.deepClone(this.form.config.attrs.children.value)
            }
        },
        watch: {
            form (val) {
                this.formList = tools.deepClone(val.config.attrs.children.value)
            }
        },
        methods: {
            onAddHander () {
                const formCopy = tools.deepClone(this.form)
                formCopy.config.attrs.children.value = tools.deepClone(this.formList)
                this.$emit('combineAdded', this.index, formCopy)
            },
            onSortHandler (evt) {
                if (evt.newIndex !== evt.oldIndex) {
                    const formCopy = tools.deepClone(this.form)
                    formCopy.config.attrs.children.value = tools.deepClone(this.formList)
                    this.$emit('combineAdded', this.index, formCopy)
                }
            },
            combineAdded (index, formCopy) {
                this.formList[index] = formCopy
                this.onAddHander()
            },
            onEditClick (form) {
                this.$emit('onEditClick', form)
            },
            onShowInfoClick (form) {
                this.$emit('onShowInfoClick', form)
            },
            onDeleteClick (tag_code) {
                this.$emit('onDeleteClick', tag_code)
            }
        }
    }
</script>
<style lang="scss">
.form-drag-area-inner {
    width: 100%;
    height: 100%;
}
</style>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.combine-form {
    width: 100%;
    border: 1px dotted red;
    .content-wrapper {
        position: relative;
        padding: 20px;
        width: 100%;
        border: 1px dotted transparent;
        overflow: hidden;
        cursor: move;
        &.active,
        &:hover {
            .operation-btn-group {
                display: block;
            }
        }
    }
    .form-item-label {
        float: left;
        width: 100px;
        line-height: 32px;
        font-size: 12px;
        text-align: right;
        vertical-align: middle;
    }
    .form-item-content {
        width: 100%;
        .form-drag-area-inner {
            width: 100%;
            min-height: 200px;
        }
    }
    .operation-btn-group {
        display: none;
        position: absolute;
        right: 0;
        top: 0px;
        margin-right: 10px;
        z-index: 1;
        .operation-btn {
            display: inline-block;
            cursor: pointer;
            font-size: 14px;
            color: #979ba5;
            &:not(.common-icon-horizon-line-group):hover {
                color: #63656e;
            }
            &.active {
                color: #3a84ff;
            }
            &.common-icon-box-pen {
                font-size: 12px;
            }
        }
    }
    .combine-move-icon {
        display: flex;
        align-items: center;
        position: absolute;
        left: 0;
        top: 0;
        z-index: 1;
        width: 20px;
        height: 100%;
    }
    .common-icon-horizon-line-group {
        cursor: move;
    }
    .tag-info {
        position: relative;
        margin-top: 10px;
        padding: 20px;
        color: #63656e;
        background: #ffffff;
        border-radius: 4px;
        font-size: 14px;
        box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.06);
        &:after {
            content: '';
            position: absolute;
            top: -5px;
            right: 56px;
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 0 8px 8px 8px;
            border-color: transparent transparent #ffffff transparent;
            outline: #c4c6cc;
        }
        &>h3 {
            margin: 0;
        }
        &>section {
            margin: 20px 0;
        }
        .attr-item {
            margin: 8px 0;
        }
    }
}
</style>
