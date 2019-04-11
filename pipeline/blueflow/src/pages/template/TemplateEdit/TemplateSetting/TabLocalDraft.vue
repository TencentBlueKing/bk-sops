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
    <div class="local-draft-panel">
        <div class="local-title">
            <span> {{i18n.localCache}} </span>
        </div>
        <div :class="{'add-draft': true, 'unfold-add-draft': newDraftShow}">
            <div class="draft-form" v-if="newDraftShow">
                <BaseInput :placeholder="i18n.draftMessage" name="draftName" v-model="newDraftName" v-validate="draftNameRule"/>
                <bk-button type="success" size="small" @click="onNewDraft">{{i18n.affirm}}</bk-button>
                <bk-button size="small" @click="onCancelNewDraft">{{i18n.cancel}}</bk-button>
            </div>
            <bk-button class="add-draft-btn" v-else type="default" size="small" @click="onShowDraftForm">
                {{ i18n.newDraft }}
            </bk-button>
            <bk-tooltip placement="bottom-end" class="draft-tooltip">
                <i class="bk-icon icon-info-circle"></i>
                <div slot="content">
                    <div class="tips-item" style="white-space: normal;">
                        <h4>{{ i18n.sketch }}</h4>
                        <p>
                            {{ i18n.draftSketch }}
                        </p>
                    </div>
                </div>
            </bk-tooltip>
            <span class="common-error-tip error-msg">{{ errors.first('draftName') }}</span>
        </div>
        <div class="local-draft-content">
            <div class="variable-header clearfix">
                <span class="col-drag t-head"></span>
                <span class="col-number t-head">{{ i18n.serialNumber }}</span>
                <span class="col-message t-head">{{ i18n.draftMessage }}</span>
                <span class="col-time t-head">{{ i18n.saveTime }}</span>
                <span class="col-delete t-head"></span>
            </div>
            <ul class="draft-list">
                <draggable v-model="draftArray" :options="{handle:'.col-drag'}">
                    <li
                        v-for="(draft, index) in draftArray"
                        :key="draft.key"
                        :class="{
                            'clearfix': true,
                            'draft-item': true}"
                        @click="onReplaceTemplate(draft.data.template)">
                        <div class="draft-content">
                            <span class="col-item col-drag"></span>
                            <span class="col-item col-number"> {{index + 1}} </span>
                            <span class="col-item col-message" :title="draft.data.description.message"> {{draft.data.description.message}}</span>
                            <span class="col-item col-time"> {{draft.data.description.time}}</span>
                            <span class="col-item col-delete" @click.stop="onDeleteDraft(draft.key)">
                                <i class="bk-icon icon-close-circle"></i>
                            </span>
                        </div>
                    </li>
                </draggable>
                <li v-if="!draftArray.length" class="empty-draft-tip">
                    <NoData>
                        <p>{{i18n.emptyDraftTip}}</p>
                    </NoData>
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
import '@/utils/i18n.js'
import draggable from 'vuedraggable'
import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
import BaseInput from '@/components/common/base/BaseInput.vue'
import NoData from '@/components/common/base/NoData.vue'

export default {
    name: 'TabLocalDraft',
    components: {
        draggable,
        BaseInput,
        NoData
    },
    props: ['draftArray'],
    data () {
        return {
            replaceData: null,
            newDraftShow: false,
            newDraftName: '',
            draftNameRule: {
                required: true,
                max: STRING_LENGTH.DRAFT_NAME_MAX_LENGTH,
                regex: NAME_REG
            },
            i18n: {
                localCache: gettext('本地缓存'),
                newDraft: gettext('新建'),
                draftMessage: gettext('名称'),
                replace: gettext('替换'),
                saveTime: gettext('保存时间'),
                delete: gettext('删除'),
                emptyDraftTip: gettext('无数据，请手动添加缓存或等待自动保存'),
                replaceTips: gettext('替换模板'),
                replaceConfirm: gettext('是否替换模板？'),
                serialNumber: gettext('序号'),
                draftName: gettext('名称'),
                sketch: gettext('简述：'),
                draftSketch: gettext('本地缓存可以用于记录当前流程所有信息，包括流程的节点编排、全局变量、名称、基础属性等信息。本地缓存支持每个流程最多保存50个最近记录，该数据存储至本地浏览器中，每个用户只能查看和编辑自己的本地缓存。'),
                affirm: gettext('保存'),
                cancel: gettext('取消'),
                resetTemplate: gettext('重置模板')
            }
        }
    },
    methods: {
        // 单击模板记录
        onReplaceTemplate (templateData) {
            if (!this.isClickDraft) {
                this.$emit('updateLocalTemplateData')
            }
            const data = {
                templateData: templateData,
                type: 'replace'
            }
            this.$emit('onReplaceTemplate', data)
            this.$emit('hideConfigPanel')
        },
        // 删除本地缓存
        onDeleteDraft (key) {
            this.$emit('onDeleteDraft', key)
        },
        // 新增本地缓存
        onShowDraftForm () {
            this.newDraftShow = true
            this.$emit('hideConfigPanel')
        },
        onNewDraft () {
            this.$validator.validateAll().then((result) => {
                if (!result) {
                    return
                }
                this.$emit('onNewDraft', this.newDraftName)
                this.newDraftName = ''
                this.newDraftShow = false
                this.$emit('hideConfigPanel')
            })
        },
        onCancelNewDraft () {
            this.newDraftName = ''
            this.newDraftShow = false
        }
    }
}
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.local-draft-panel {
    height: 100%;
     .local-title {
        height: 35px;
        margin: 20px;
        border-bottom: 1px solid #cacecb;
        span {
            font-size: 14px;
            font-weight:600;
            color:#313238;
        }
    }
    .add-draft {
        margin: 20px;
        .draft-form {
            display: inline-block;
            input {
                width: 200px;
            }
            .operate-btn {
                padding: 0 5px;
                color: $blueDefault;
                white-space: nowrap;
                cursor: pointer;
                &:first-child {
                    padding-left: 20px;
                }
            }
            .operate-btn:nth-child(2) {
                padding-left: 15px;
            }
            .base-input {
                height: 32px;
                line-height: 32px;
                padding-bottom: 2px;
            }
        }
        .add-draft-btn {
            width: 90px;
            height: 32px;
            line-height: 32px;
        }
    }
    .draft-tooltip {
        float: right;
        margin-top: 8px;
        .icon-info-circle {
            color:#c4c6cc;
            cursor: pointer;
            &:hover {
                color: #f4aa1a;
            }
        }
        /deep/ .bk-tooltip-popper {
            .tips-item {
                margin-bottom: 20px;
                &:last-child {
                    margin-bottom: 0;
                }
                h4 {
                    margin-top: 0;
                    margin-bottom: 10px;
                }
                p {
                    white-space: normal;
                    word-wrap: break-word;
                    word-break: break-all;
                }
            }
            .tips-item-content {
                margin-bottom: 20px;
                &:last-child {
                    margin-bottom: 0;
                }
                h4 {
                    margin-top: 0;
                    margin-bottom: 10px;
                }
                p {
                    margin-top: -18px;
                }
            }
            .bk-tooltip-arrow {
                right: 2px;
            }
            .bk-tooltip-inner {
                 margin-right: -18px;
            }
        }
    }
    .local-draft-content {
        height: calc(100% - 54px);
        border-top: 1px solid $commonBorderColor;
    }
    .variable-header {
        .t-head {
            float: left;
            padding: 0 8px;
            height: 40px;
            line-height: 40px;
            font-size: 14px;
            border-bottom: 1px solid $commonBorderColor;
            background: $greyDash;
        }
    }
    .draft-list {
        width: 100%;
        height: calc(100% - 40px);
        text-align: center;
        overflow-x: hidden;
        overflow-y: auto;
        @include scrollbar;
        .draft-item {
            border-bottom: 1px solid #ebebeb;
            background: $whiteDefault;
            cursor: pointer;
            &:hover {
                background: $blueStatus;
            }
            .variable-content, .draft-content {
                display: table;
                &:hover{
                    .icon-close-circle {
                        display: inline-block;
                    }
                }
            }
            .col-item {
                display: table-cell;
                padding: 14px 4px;
                font-size: 12px;
                vertical-align: middle;
                word-break: break-all;
            }
            &.variable-editing {
                background: $blueStatus;
            }
            .col-source {
                font-size: 16px;
            }
            .col-show-type {
                font-size: 18px;
            }
            .col-delete {
                .icon-close-circle {
                    display: none;
                }
            }
            .col-time {
                width: 134px;
                text-align: center;
            }
            .col-replace {
                width: 45px;
            }
            .col-number {
                width: 45px;
            }
        }
        .variable-edit-td {
            padding: 0;
            width: 412px;
        }
        .empty-draft-tip {
            margin-top: 120px;
        }
    }
    .variable-header, .draft-list {
        font-size: 12px;
        .col-drag {
            width: 20px;
            padding: 10px 0;
            cursor: move;
        }
        .col-name {
            width: 107px;
            text-align: left;
        }
        .draft-item  {
            .col-message {
                display: block;
            }
        }
        .col-source {
            width: 45px;
        }
        .col-show-type {
            width: 45px;
        }
        .col-delete {
            width: 45px;
        }
        .col-output {
            width: 57px;
            text-align: center;
        }
        .col-message {
            width: 153px;
            text-align: center;
            overflow: hidden;
            text-overflow: ellipsis;
            word-break: break-all;
            white-space: nowrap;
        }
        .col-delete {
            width: 45px;
            text-align: center;
        }
        .col-time {
            width: 150px;
            text-align: center;
        }
        .col-replace {
            width: 45px;
        }
        .col-number {
            width: 50px;
        }
    }
    .config-wrapper {
        padding: 20px;
        .common-form-item > label {
            width: 70px;
            font-weight: normal;
        }
        .common-form-content {
            margin-left: 90px;
            line-height: 32px;
        }
        .el-checkbox {
            margin-left: 0;
            margin-right: 14px;
        }
        /deep/ .el-checkbox__input.is-checked + .el-checkbox__label {
            color: $greyDefault;
        }
    }
    .draft-dialog-content {
        margin-left: -30px;
    }
}
</style>
