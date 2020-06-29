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
    <div class="template-snapshoot-panel">
        <bk-sideslider
            ext-cls="common-template-setting-sideslider"
            :width="800"
            :is-show="isShow"
            :before-close="onBeforeClose"
            :quick-close="true">
            <div slot="header">
                <span> {{$t('本地快照')}} </span>
                <i class="common-icon-info snapshoot-tooltip"
                    v-bk-tooltips="{
                        allowHtml: true,
                        content: $t('可自动保存最近的50次快照，每5分钟一次。仅在本地浏览器存储。'),
                        placement: 'bottom-end',
                        duration: 0,
                        width: 400 }">
                </i>
            </div>
            <div class="content-wrap" slot="content">
                <div class="local-snapshoot-content">
                    <table class="snapshoot-table">
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
                                <td class="col-number">--</td>
                                <td class="col-name">--</td>
                                <td class="col-time">--</td>
                                <td class="col-operation-group">
                                    <bk-button size="small" theme="default" @click="onCreateSnapshoot">{{ $t('新建') }}</bk-button>
                                </td>
                            </tr>
                            <tr
                                v-for="(item, index) in snapshoots"
                                :key="item.timestamp">
                                <td class="col-number">
                                    <div class="content">{{ snapshoots.length - index }}</div>
                                </td>
                                <td
                                    class="col-name"
                                    :title="item.name">
                                    <div class="content">
                                        <bk-input
                                            v-if="editingData.key === item.timestamp"
                                            v-model="editingData.name"
                                            v-focus
                                            v-validate="nameRule"
                                            data-vv-validate-on=" "
                                            class="snapshoot-name-input"
                                            :name="'snapshootName' + item.timestamp"
                                            :placeholder="$t('名称')"
                                            @blur="onSaveName(item)"
                                            @enter="onSaveName(item)" />
                                        <span v-else>{{item.name}}</span>
                                        <i class="common-icon-edit" @click.stop="onEditName(item)"></i>
                                        <span
                                            v-if="errors.first('snapshootName' + item.timestamp)"
                                            class="common-icon-info error-msg"
                                            v-bk-tooltips="{
                                                content: errors.first('snapshootName' + item.timestamp),
                                                placements: ['top-end']
                                            }">
                                        </span>
                                    </div>
                                </td>
                                <td class="col-time"><div class="content">{{item.timestamp | timestampToDatetime}}</div></td>
                                <td class="col-operation-group">
                                    <span class="operation-item" @click="onUseSnapshoot(item, snapshoots.length - index)">{{$t('还原')}}</span>
                                </td>
                            </tr>
                            <tr v-if="!snapshoots.length" class="empty-snapshoot-tip">
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
    import moment from 'moment'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TabTemplateSnapshoot',
        components: {
            NoData
        },
        filters: {
            timestampToDatetime (val) {
                return moment.unix(val / 1000).format('YYYY-MM-DD HH:mm:ss')
            }
        },
        props: {
            isShow: Boolean,
            snapshoots: Array
        },
        data () {
            return {
                editingData: {
                    key: null,
                    name: ''
                },
                nameRule: {
                    required: true,
                    max: STRING_LENGTH.DRAFT_NAME_MAX_LENGTH,
                    regex: NAME_REG
                }
            }
        },
        methods: {
            // 新建快照
            onCreateSnapshoot () {
                this.$emit('createSnapshoot')
            },
            // 还原快照
            onUseSnapshoot (snapshoot, index) {
                this.$emit('useSnapshoot', snapshoot.template, index)
            },
            // 点击编辑快照名称
            onEditName (snapshoot) {
                this.editingData.key = snapshoot.timestamp
                this.editingData.name = snapshoot.name
            },
            // 保存编辑中的快照名称
            onSaveName (snapshoot) {
                this.$validator.validateAll().then((result) => {
                    if (!result) {
                        return
                    }
                    const data = { ...snapshoot, name: this.editingData.name }
                    this.$emit('updateSnapshoot', data)
                    this.editingData.key = null
                    this.editingData.name = ''
                })
            },
            onBeforeClose () {
                this.$emit('onColseTab', 'tplSnapshootTab')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';

.template-snapshoot-panel {
    height: 100%;
    .content-wrap {
        height: 100%;
    }
    .snapshoot-tooltip {
        display: inline-block;
        vertical-align: middle;
        margin-left: 6px;
        color:#c4c6cc;
        cursor: pointer;
        &:hover {
            color: #f4aa1a;
        }
    }
    .local-snapshoot-content {
        padding: 26px 28px;
        padding-bottom: 0;
        height: 100%;
    }
    .snapshoot-table {
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
            tr:not(.empty-snapshoot-tip):hover {
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
        .empty-snapshoot-tip {
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
