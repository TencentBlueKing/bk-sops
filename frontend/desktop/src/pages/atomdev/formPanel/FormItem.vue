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
    <div class="form-item-wrap">
        <div :class="['content-wrapper', { active: tagInfo && tagInfo.tagCode === form.config.tag_code }]">
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
                    @click="$emit('onShowInfoClick',form)">
                </i>
                <i class="operation-btn common-icon-box-pen" @click="$emit('onEditClick', form)"></i>
                <i class="operation-btn bk-icon common-icon-close-linear-circle" @click="$emit('onDeleteClick',form.config.tag_code)"></i>
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
    import tools from '@/utils/tools.js'
    import FormNotFound from './FormNotFound.vue'
    import importTag from '../importTag.js'
    const { components: TAGS } = importTag()
    export default {
        name: 'FormItem',
        components: {
            FormNotFound,
            ...TAGS
        },
        props: {
            tagInfo: {
                type: Object
            },
            form: {
                type: Object
            }
        },
        data () {
            return {
                i18n: {
                    attr: gettext('属性')
                }
            }
        },
        methods: {
            getFormProps (config) {
                const formProps = {}
                Object.keys(config.attrs).reduce((acc, cur) => {
                    formProps[cur] = tools.deepClone(config.attrs[cur].value)
                }, formProps)
                return Object.assign(formProps, { tagCode: config.tag_code })
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
.form-item-wrap{
    .content-wrapper {
        position: relative;
        padding: 10px 100px 10px 0;
        border: 1px dotted transparent;
        overflow: hidden;
        cursor: move;
        &.active,
        &:hover {
            border-color: #c4c6cc;
            border-radius: 4px;
            background: #f0f2f5;
            .content-mask .operation-btn {
                display: inline-block;
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
        margin-left: 120px;
        min-height: 32px;
    }
    .content-mask {
        display: flex;
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 100%;
        background: transparent;
        justify-content: flex-end;
        align-items: center;
        text-align: right;
        z-index: 1;
        .operation-btn {
            display: none;
            color: #979ba5;
            margin-right: 10px;
            font-size: 14px;
            cursor: pointer;
            &:not(.common-icon-horizon-line-group):hover {
                color: #63656e;
            }
            &.active {
                color: #3a84ff;
            }
            &.common-icon-box-pen {
                font-size: 12px;
            }
            &.common-icon-horizon-line-group {
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                cursor: move;
            }
        }
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
