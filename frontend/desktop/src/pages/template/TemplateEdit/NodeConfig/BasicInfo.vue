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
        <!-- 普通插件 -->
        <bk-form
            v-if="!isSubflow"
            :label-width="130"
            :model="formData">
            <bk-form-item :label="i18n.plugin" :required="true">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div class="group-text choose-plugin-btn"
                            @click.stop="openSelectorPanel">{{ formData.plugin ? i18n.reselect : i18n.select }}</div>
                    </template>
                </bk-input>
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
                        v-for="item in versionList"
                        :key="item.version"
                        :id="item.version"
                        :name="item.version">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item :label="i18n.nodeName" :required="true">
                <bk-input v-model="formData.nodeName" @blur="saveBasicInfo"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.errorHandle" class="error-handle">
                <bk-checkbox v-model="formData.ignorable" @change="onErrorIgnoreChange">
                    <i class="error-handle-icon common-icon-dark-circle-i"></i>
                    {{ i18n.ignorable }}
                </bk-checkbox>
                <bk-checkbox v-model="formData.skippable" :disabled="formData.ignorable" @change="saveBasicInfo">
                    <i class="error-handle-icon common-icon-dark-circle-s"></i>
                    {{ i18n.skip }}
                </bk-checkbox>
                <bk-checkbox v-model="formData.retryable" :disabled="formData.ignorable" @change="saveBasicInfo">
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
                <bk-switcher v-model="formData.selectable" size="small" @change="saveBasicInfo"></bk-switcher>
            </bk-form-item>
        </bk-form>
        <!-- 子流程 -->
        <bk-form
            v-else
            :label-width="130"
            :model="formData">
            <bk-form-item :label="i18n.tpl" :required="true">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div class="group-text choose-plugin-btn"
                            @click.stop="openSelectorPanel">{{ formData.tpl ? i18n.reselect : i18n.select }}</div>
                    </template>
                </bk-input>
                <!-- 子流程版本更新 -->
                <i
                    :class="[
                        'common-icon-clock-inversion',
                        'update-tooltip',
                        { 'disabled': inputLoading }
                    ]"
                    v-if="subflowHasUpdate"
                    v-bk-tooltips="{
                        content: i18n.update,
                        placements: ['bottom-end'] }"
                    @click="onUpdateSubflowVersion">
                </i>
            </bk-form-item>
            <bk-form-item :label="i18n.nodeName" :required="true">
                <bk-input v-model="formData.nodeName"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.selectable">
                <bk-switcher v-model="formData.selectable" size="small"></bk-switcher>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations } from 'vuex'
    export default {
        name: 'BasicInfo',
        props: {
            formData: {
                type: Object,
                default () {
                    return {}
                }
            },
            versionList: {
                type: Array,
                default () {
                    return []
                }
            },
            nodeConfig: {
                type: Object,
                default () {
                    return {}
                }
            },
            name: {
                type: String,
                default: ''
            },
            isSubflow: {
                type: Boolean,
                default: false
            },
            inputLoading: {
                type: Boolean,
                default: false
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
                    select: gettext('选择'),
                    reselect: gettext('重选'),
                    plugin: gettext('标准插件'),
                    version: gettext('插件版本'),
                    update: gettext('版本更新'),
                    nodeName: gettext('节点名称'),
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
        computed: {
            ...mapState({
                'subprocessInfo': state => state.template.subprocess_info
            }),
            subflowHasUpdate () {
                return this.subprocessInfo.details.some(subflow => {
                    if (
                        subflow.expired
                        && subflow.template_id === Number(this.nodeConfig.template_id)
                        && subflow.subprocess_node_id === this.nodeConfig.id
                    ) {
                        return true
                    }
                })
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setNodeBasicInfo'
            ]),
            onErrorIgnoreChange (val) {
                if (val) {
                    this.formData.retryable = false
                    this.formData.skippable = false
                }
                this.saveBasicInfo()
            },
            saveBasicInfo () {
                const {
                    name,
                    ignorable,
                    skippable,
                    retryable,
                    selectable
                } = this.formData
                this.setNodeBasicInfo({
                    id: this.nodeConfig.id,
                    setVals: {
                        name,
                        ignorable,
                        skippable,
                        retryable,
                        selectable
                    }
                })
            },
            openSelectorPanel () {
                this.$emit('openSelectorPanel')
            },
            /**
             * 子流程版本更新
             */
            onUpdateSubflowVersion () {
                
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
        .choose-plugin-btn {
            line-height: 30px;
            color: #3a84ff;
            background: #e1ecff;
            cursor: pointer;
        }
        .update-tooltip {
            position: absolute;
            right: -28px;
            top: 8px;
            cursor: pointer;
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
