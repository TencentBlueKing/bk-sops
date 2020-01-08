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
    <div class="basic-info">
        <bk-form
            v-if="formData.type === 'ServiceActivity'"
            :label-width="130"
            :model="formData">
            <bk-form-item :label="i18n.plugin" :required="true">
                <bk-select
                    v-model="formData.plugin"
                    :clearable="false"
                    :searchable="true"
                    @selected="$emit('pluginChange')">
                    <bk-option
                        v-for="atom in atomList"
                        :key="atom.code"
                        :id="atom.code"
                        :name="`${atom.type}-${atom.name}`">
                    </bk-option>
                </bk-select>
                <i class="common-icon-info form-item-tips"
                    v-if="formData.desc"
                    v-bk-tooltips="{
                        content: formData.desc,
                        width: '400',
                        placements: ['bottom-end'] }">
                </i>
            </bk-form-item>
            <bk-form-item :label="i18n.version" :required="true">
                <bk-select
                    v-model="formData.version"
                    :clearable="false"
                    @selected="$emit('versionChange')">
                    <bk-option
                        v-for="item in formData.versionList"
                        :key="item.version"
                        :id="item.version"
                        :name="item.version">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item :label="i18n.name" :required="true">
                <bk-input v-model="formData.name"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.step">
                <bk-input v-model="formData.step"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.errorHandle" class="error-handle">
                <bk-checkbox v-model="formData.ignorable" @change="onErrorIgnoreChange">
                    <i class="error-handle-icon common-icon-dark-circle-i"></i>
                    {{ i18n.ignorable }}
                </bk-checkbox>
                <bk-checkbox v-model="formData.skippable" :disabled="formData.ignorable">
                    <i class="error-handle-icon common-icon-dark-circle-s"></i>
                    {{ i18n.skip }}
                </bk-checkbox>
                <bk-checkbox v-model="formData.retryable" :disabled="formData.ignorable">
                    <i class="error-handle-icon common-icon-dark-circle-r"></i>
                    {{ i18n.retry }}
                </bk-checkbox>
                <p
                    v-if="!formData.ignorable && !formData.skippable && !formData.retryable"
                    class="error-handle-tips">
                    {{ i18n.errorHandleTip }}
                </p>
                <div id="html-error-ingored-tootip" class="tips-item" style="white-space: normal;">
                    <p>{{ i18n.ignoreTip }}</p>
                    <p>{{ i18n.skipTip }}</p>
                    <p>{{ i18n.retryTip }}</p>
                </div>
                <i v-bk-tooltips="errorHandleTipsConfig" ref="tooltipsHtml" class="common-icon-info form-item-tips"></i>
            </bk-form-item>
            <bk-form-item :label="i18n.selectable">
                <bk-switcher v-model="formData.selectable" size="small"></bk-switcher>
            </bk-form-item>
        </bk-form>
        <bk-form
            v-else
            :label-width="130"
            :model="formData">
            <bk-form-item :label="i18n.tpl" :required="true">
                <bk-select
                    v-model="formData.tpl"
                    :clearable="false"
                    :searchable="true"
                    @selected="$emit('tplChange')">
                    <bk-option
                        v-for="item in subflowList"
                        :key="item.id"
                        :id="item.id"
                        :name="item.name">
                        <template>
                            <span class="subflow-option-name">{{item.name}}</span>
                            <i class="bk-icon common-icon-box-top-right-corner open-link-icon" @click.stop="onOpenTpl"></i>
                        </template>
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item :label="i18n.name" :required="true">
                <bk-input v-model="formData.name"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.step">
                <bk-input v-model="formData.step"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.selectable">
                <bk-switcher v-model="formData.selectable" size="small"></bk-switcher>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import '@/utils/i18n.js'

    export default {
        name: 'BasicInfo',
        props: {
            formData: {
                type: Object,
                default () {
                    return {}
                }
            },
            atomList: {
                type: Array,
                default () {
                    return []
                }
            },
            subflowList: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                errorHandleTipsConfig: {
                    allowHtml: true,
                    width: 400,
                    content: '#html-error-ingored-tootip',
                    placement: 'bottom-end'
                },
                i18n: {
                    plugin: gettext('标准插件'),
                    version: gettext('插件版本'),
                    name: gettext('节点名称'),
                    step: gettext('步骤名称'),
                    errorHandle: gettext('失败处理'),
                    selectable: gettext('是否可选'),
                    ignorable: gettext('自动忽略'),
                    skip: gettext('手动跳过'),
                    retry: gettext('手动重试'),
                    tpl: gettext('流程模板'),
                    errorHandleTip: gettext('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续'),
                    explanation: gettext('说明：'),
                    ignoreTip: gettext('自动忽略：标准插件节点如果执行失败，会自动忽略错误并把节点状态设置为成功。'),
                    skipTip: gettext('手动跳过：标准插件节点如果执行失败，可以人工干预，直接跳过节点的执行。'),
                    retryTip: gettext('手动重试：标准插件节点如果执行失败，可以人工干预，填写参数后重试节点。')
                }
            }
        },
        methods: {
            onOpenTpl () {},
            onErrorIgnoreChange (val) {
                if (val) {
                    this.formData.retryable = false
                    this.formData.skippable = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .basic-info {
        padding-right: 30px;
    }
    .error-handle {
        /deep/ .bk-form-checkbox {
            margin-right: 30px;
            &.is-disabled .bk-checkbox-text {
                color: #c4c6cc;
            }
        }
        .error-handle-icon {
            padding-right: 4px;
            color: #a6b0c7;
        }
        .error-handle-tips {
            font-size: 12px;
            line-height: 1;
            color: #ffb400;
        }
    }
    /deep/ .bk-form {
        .bk-label {
            font-size: 12px;
        }
        .bk-checkbox-text {
            font-size: 12px;
            color: #63656e;
        }
        .form-item-tips {
            position: absolute;
            right: -30px;
            top: 7px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
    }
    .bk-option-content {
        &:hover {
            .open-link-icon {
                display: inline-block;
            }
        }
        .open-link-icon {
            display: none;
            float: right;
            margin-top: 10px;
        }
    }
</style>
