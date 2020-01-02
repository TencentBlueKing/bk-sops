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
    <div class="local-draft-panel">
        <div class="local-title">
            <span> {{i18n.localCache}} </span>
            <i class="common-icon-info draft-tooltip"
                v-bk-tooltips="{
                    allowHtml: true,
                    content: '#draft-desc',
                    placement: 'bottom-end',
                    duration: 0,
                    width: 400 }"></i>
            <div id="draft-desc">
                <div class="tips-item" style="white-space: normal;">
                    <h4>{{ i18n.sketch }}</h4>
                    <p>{{ i18n.draftSketch }}</p>
                </div>
            </div>
        </div>
        <div :class="{ 'add-draft': true, 'unfold-add-draft': newDraftShow }">
            <div class="draft-form" v-if="newDraftShow">
                <bk-input
                    name="draftName"
                    class="draft-name-input"
                    :placeholder="i18n.draftMessage"
                    v-model="newDraftName"
                    data-vv-validate-on=" "
                    v-validate="draftNameRule" />
                <bk-button theme="success" @click="onNewDraft">{{i18n.affirm}}</bk-button>
                <bk-button @click="onCancelNewDraft">{{i18n.cancel}}</bk-button>
            </div>
            <bk-button class="add-draft-btn" v-else theme="default" @click="onShowDraftForm">
                {{ i18n.newDraft }}
            </bk-button>
            <span class="common-error-tip error-msg">{{ errors.first('draftName') }}</span>
        </div>
        <div class="local-draft-content">
            <table class="draft-table">
                <thead>
                    <tr>
                        <th class="col-number">{{ i18n.serialNumber }}</th>
                        <th class="col-name">{{ i18n.draftMessage }}</th>
                        <th class="col-time">{{ i18n.saveTime }}</th>
                        <th class="col-delete"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr
                        v-for="(draft, index) in draftArray"
                        :key="draft.key"
                        @click="onReplaceTemplate(draft.data.template)">
                        <td class="col-number"><div class="content">{{ index + 1 }}</div></td>
                        <td
                            class="col-name"
                            :title="draft.data.description.message">
                            <div class="content">{{draft.data.description.message}}</div>
                        </td>
                        <td class="col-time"><div class="content">{{draft.data.description.time}}</div></td>
                        <td class="col-delete" @click.stop="onDeleteDraft(draft.key)">
                            <i class="close-btn common-icon-dark-circle-close"></i>
                        </td>
                    </tr>
                    <tr v-if="!draftArray.length" class="empty-draft-tip">
                        <td><NoData><p>{{i18n.emptyDraftTip}}</p></NoData></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TabLocalDraft',
        components: {
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
.tips-item {
    & > h4 {
        margin: 0;
    }
}
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
            .draft-name-input {
                display: inline-block;
                width: 200px;
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
        display: inline-block;
        vertical-align: middle;
        margin-left: 6px;
        color:#c4c6cc;
        cursor: pointer;
        &:hover {
            color: #f4aa1a;
        }
    }
    .local-draft-content {
        height: calc(100% - 54px);
        border-top: 1px solid $commonBorderColor;
    }
    .draft-table {
        width: 100%;
        height: 100%;
        color: #313238;
        border-collapse: collapse;
        table-layout: fixed;
        tr {
            display: block;
        }
        th, td {
            padding: 0 10px;
            height: 40px;
            line-height: 40px;
            border-bottom: 1px solid $commonBorderColor;
            text-align: left;
        }
        th {
            font-size: 14px;
            font-weight: normal;
            background: #ecf0f4;
        }
        td {
            font-size: 12px;
            .content {
                width: 100%;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
        }
        tbody {
            display: block;
            height: calc(100% - 40px);
            overflow: auto;
            tr:not(.empty-draft-tip):hover {
                background: $blueStatus;
                cursor: pointer;
                .close-btn {
                    display: inline-block;
                }
            }
        }
        .col-number {
            padding-left: 20px;
            width: 80px;
            max-width: 80px;
        }
        .col-name {
            width: 174px;
            max-width: 174px;
        }
        .col-time {
            width: 146px;
        }
        .col-delete {
            position: relative;
            width: 20px;
            .close-btn {
                display: none;
                position: absolute;
                top: 13px;
                right: 14px;
                font-size: 14px;
                color: #c4c6cc;
                cursor: pointer;
                &:hover {
                    color: #979ba5;
                }
            }
        }
        .empty-draft-tip {
            td {
                width: 419px;
                border-bottom: none;
            }
            .no-data-wrapper {
                margin-top: 120px;
                line-height: 1;
            }
        }
        .common-icon-dark-circle-close:hover {
            color: #cecece;
        }
    }
}
.tooltip-content {
    margin-bottom: 20px;
    &:last-child {
        margin-bottom: 0;
    }
    h4 {
        margin-top: 0;
        margin-bottom: 10px;
    }
}
</style>
