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
        <bk-sideslider
            ext-cls="common-template-setting-sideslider"
            :width="800"
            :is-show="isShow"
            :before-close="onBeforeClose"
            :quick-close="true">
            <div slot="header">
                <span> {{$t('本地快照')}} </span>
                <i class="common-icon-info draft-tooltip"
                    v-bk-tooltips="{
                        content: $t('可自动保存最近的50次快照，每5分钟一次。仅在本地浏览器存储。'),
                        placement: 'bottom-end',
                        duration: 0,
                        width: 400 }">
                </i>
            </div>
            <div class="content-wrap" slot="content">
                <div class="local-draft-content">
                    <table class="draft-table">
                        <thead>
                            <tr>
                                <th class="col-number">{{ $t('序号') }}</th>
                                <th class="col-name">{{ $t('名称') }}</th>
                                <th class="col-time">{{ $t('保存时间') }}</th>
                                <th class="col-operation-group">{{ $t('操作') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="background: #f0f1f5">
                                <td class="col-number">{{ draftArray.length + 1 }}</td>
                                <td class="col-name">—</td>
                                <td class="col-time">—</td>
                                <td class="col-operation-group">
                                    <bk-button size="small" theme="default" @click="onNewDraft">{{ $t('新建') }}</bk-button>
                                </td>
                            </tr>
                            <tr
                                v-for="(draft, index) in draftArray"
                                :key="draft.key">
                                <td class="col-number">
                                    <div class="content">{{ draftArray.length - index }}</div>
                                </td>
                                <td
                                    class="col-name"
                                    :title="draft.data.description.message">
                                    <div class="content">
                                        <bk-input
                                            v-if="editingDraf.key === draft.key"
                                            v-model="editingDraf.name"
                                            v-focus
                                            v-validate="draftNameRule"
                                            data-vv-validate-on=" "
                                            class="draft-name-input"
                                            :name="'draftName' + draft.key"
                                            :placeholder="$t('名称')"
                                            @blur="saveDraftnName(draft)"
                                            @enter="saveDraftnName(draft)" />
                                        <span v-else>{{draft.data.description.message}}</span>
                                        <i class="common-icon-edit" @click.stop="onEditDraftnName(draft)"></i>
                                        <span
                                            v-if="errors.first('draftName' + draft.key)"
                                            class="common-icon-info error-msg"
                                            v-bk-tooltips="{
                                                content: errors.first('draftName' + draft.key),
                                                placements: ['top-end']
                                            }">
                                        </span>
                                    </div>
                                </td>
                                <td class="col-time"><div class="content">{{draft.data.description.time}}</div></td>
                                <td class="col-operation-group">
                                    <span class="operation-item" @click="onReplaceTemplate(draft.data.template, draftArray.length - index)">{{$t('还原')}}</span>
                                </td>
                            </tr>
                            <tr v-if="!draftArray.length" class="empty-draft-tip">
                                <td><NoData><p>{{$t('无数据，请手动添加快照或等待自动保存')}}</p></NoData></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </bk-sideslider>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TabLocalDraft',
        components: {
            NoData
        },
        props: {
            draftArray: Array,
            isShow: Boolean
        },
        data () {
            return {
                editingDraf: {
                    key: null,
                    name: ''
                },
                replaceData: null,
                newDraftShow: false,
                draftNameRule: {
                    required: true,
                    max: STRING_LENGTH.DRAFT_NAME_MAX_LENGTH,
                    regex: NAME_REG
                }
            }
        },
        methods: {
            // 新建快照
            onNewDraft () {
                this.$emit('hideConfigPanel')
                this.$emit('onNewDraft', i18n.t('新建快照'))
            },
            // 还原快照
            onReplaceTemplate (templateData, index) {
                if (!this.isClickDraft) {
                    this.$emit('updateLocalTemplateData')
                }
                const data = {
                    templateData: templateData,
                    type: 'replace',
                    index: index
                }
                this.$emit('onReplaceTemplate', data)
                this.$emit('hideConfigPanel')
            },
            // 删除快照
            onDeleteDraft (key) {
                this.$emit('onDeleteDraft', key)
            },
            // 点击编辑快照
            onEditDraftnName (draft) {
                this.editingDraf.key = draft.key
                this.editingDraf.name = draft.data.description.message
            },
            // 保存编辑后的快照
            saveDraftnName (draft) {
                this.$validator.validateAll().then((result) => {
                    if (!result) {
                        return
                    }
                    const newData = tools.deepClone(draft.data)
                    newData.description.message = this.editingDraf.name
                    this.$emit('updateDraft', this.editingDraf.key, newData)
                    this.editingDraf.key = null
                    this.editingDraf.name = ''
                })
            },
            onBeforeClose () {
                this.$emit('onColseTab', 'localDraftTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.local-draft-panel {
    height: 100%;
    .content-wrap {
        height: 100%;
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
        padding: 26px 28px;
        padding-bottom: 0;
        height: 100%;
    }
    .draft-table {
        width: 100%;
        height: 100%;
        color: #313238;
        border-collapse: collapse;
        table-layout: fixed;
        border: 1px solid $commonBorderColor;
        tr {
            display: block;
        }
        th, td {
            padding: 0 10px;
            height: 42px;
            line-height: 42px;
            font-size: 12px;
            border-bottom: 1px solid $commonBorderColor;
            text-align: left;
        }
        th {
            font-weight: normal;
            background: #fafbfd;
        }
        td {
            .content {
                position: relative;
                width: 100%;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
        }
        tbody {
            display: block;
            height: 100%;
            color: #63656e;
            overflow: auto;
            @include scrollbar;
            tr:not(.empty-draft-tip):hover {
                background: $blueStatus;
                .col-name .common-icon-edit {
                    display: inline-block;
                }
            }
        }
        .col-number {
            padding-left: 20px;
            width: 140px;
        }
        .col-name {
            width: 382px;
            .common-icon-edit {
                display: none;
                cursor: pointer;
                color: #979ba5;
                &:hover {
                    color: #63656e;
                }
            }
            .common-icon-info {
                position: absolute;
                right: 4px;
                top: 14px;
                font-size: 16px;
                color: #ea3636;
            }
        }
        .col-time {
            width: 140px;
        }
        .col-operation-group {
            width: 80px;
            .operation-item {
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .empty-draft-tip {
            td {
                width: 742px;
                border-bottom: none;
            }
            .no-data-wrapper {
                margin-top: 120px;
                line-height: 1;
                /deep/ .no-data-wording {
                    font-size: 12px;
                }
            }
        }
        .common-icon-dark-circle-close:hover {
            color: #cecece;
        }
    }
}
</style>
