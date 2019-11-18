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
    <bk-dialog
        width="850"
        :ext-cls="'common-dialog'"
        :title="i18n.title"
        :mask-close="false"
        :value="isAddCollectionDialogShow"
        :header-position="'left'"
        :auto-close="false"
        @confirm="onConfirm"
        @cancel="onCancel">
        <div class="export-container" v-bkloading="{ isLoading: businessInfoLoading, opacity: 1 }">
            <div class="template-wrapper">
                <div class="search-wrapper">
                    <bk-search-select
                        ref="bkSearchSelect"
                        :filter="true"
                        :show-condition="false"
                        :data="showFilterList"
                        v-model="searchValue"
                        @change="onSearchChange">
                    </bk-search-select>
                </div>
                <div class="template-list" v-bkloading="{ isLoading: collectionPending, opacity: 1 }">
                    <ul class="grouped-list">
                        <template v-for="group in panelList">
                            <li
                                v-if="group.children.length"
                                :key="group.id"
                                class="template-group">
                                <h5 class="group-name">
                                    {{group.name}}
                                    (<span class="list-count">{{group.children.length}}</span>)
                                </h5>
                                <ul>
                                    <li
                                        v-for="template in group.children"
                                        :key="template.id"
                                        :title="template.name"
                                        :class="[
                                            'template-item',
                                            {
                                                'template-item-selected': getTplIndexInSelected(template) > -1,
                                                'permission-disable': !hasPermission(['export'], template.auth_actions, tplOperations)
                                            }
                                        ]"
                                        @click="onSelectTemplate(template)">
                                        <div class="template-item-icon">{{getTemplateIcon(template)}}</div>
                                        <div class="item-name-box">
                                            <div class="template-item-name">{{template.name}}</div>
                                        </div>
                                        <div class="apply-permission-mask">
                                            <bk-button theme="primary" size="small">{{i18n.applyPermission}}</bk-button>
                                        </div>
                                    </li>
                                </ul>
                            </li>
                        </template>
                        <NoData v-if="!panelList.length" class="empty-template"></NoData>
                    </ul>
                </div>
            </div>
            <div class="selected-wrapper">
                <div class="selected-area-title">
                    {{i18n.selected}}
                    <span class="select-count">{{selectedList.length}}</span>
                    {{i18n.num}}
                </div>
                <ul class="selected-list">
                    <li
                        class="selected-item"
                        v-for="template in selectedList"
                        :key="template.id">
                        <div class="selected-item-icon">
                            <span class="selected-name" :title="template.name">{{getTemplateIcon(template)}}</span>
                        </div>
                        <div class="item-name-box">
                            <div class="selected-item-name">{{template.name}}</div>
                        </div>
                        <i class="selected-delete bk-icon icon-close-circle-shape" @click="deleteTemplate(template)"></i>
                    </li>
                </ul>
            </div>
            <div class="task-footer" v-if="selectError">
                <span class="error-info">{{i18n.errorInfo}}</span>
            </div>
        </div>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import toolsUtils from '@/utils/tools.js'
    import { mapGetters, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    const FILTER_LIST = [
        {
            name: gettext('选择类型'),
            id: 'type',
            children: [
                {
                    name: gettext('公共流程'),
                    id: 'common'
                },
                {
                    name: gettext('项目流程'),
                    id: 'process'
                },
                {
                    name: gettext('周期任务'),
                    id: 'per'
                },
                {
                    name: gettext('轻应用'),
                    id: 'app_maker'
                }
            ]
        },
        {
            name: gettext('选择项目'),
            id: 'project',
            children: []
        }
    ]
    export default {
        name: 'AddCollectionDialog',
        components: {
            NoData
        },
        mixins: [permission],
        props: ['isAddCollectionDialogShow', 'businessInfoLoading', 'projectInfoLoading', 'common', 'pending'],
        data () {
            return {
                i18n: {
                    num: gettext('项'),
                    delete: gettext('删除'),
                    selected: gettext('已选择'),
                    errorInfo: gettext('请选择收藏项'),
                    applyPermission: gettext('申请权限'),
                    noSearchResult: gettext('搜索结果为空')
                },
                selectError: false,
                collectionPending: false,
                panelList: [],
                selectedList: [],
                dialogFooterData: [
                    {
                        type: 'primary',
                        loading: false,
                        btnText: gettext('确认'),
                        click: 'onConfirm'
                    }, {
                        btnText: gettext('取消'),
                        click: 'onCancel'
                    }
                ],
                filterList: [],
                searchValue: [ // 搜索值
                    {
                        id: 'type',
                        name: gettext('选择类型'),
                        values: [{ id: 'common', name: '公共流程' }]
                    }
                ]
            }
        },
        computed: {
            ...mapGetters('project', {
                projectList: 'userCanViewProjects'
            }),
            showFilterList: {
                get () {
                    return this.filterList.map(m => {
                        if (m.id === 'project') {
                            m.children = this.projectList
                        }
                        return m
                    })
                },
                set (val) {
                    this.filterList = val
                }
            }
        },
        created () {
        },
        mounted () {
            this.getData()
        },
        methods: {
            ...mapActions('template/', [
                'loadTemplateCollectList'
            ]),
            async getData () {
                try {
                    const list = await this.loadTemplateCollectList()
                    console.log('list', list)
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            onConfirm () {
                
            },
            onCancel () {
                this.$emit('onCloseDialog')
            },
            /**
             *过滤已选项
             */
            filterSelectItem (baseList = this.searchValue) {
                const list = baseList.filter(m => (m.id && (m.id === 'type' || m.id === 'project')))
                switch (list.length) {
                    case 0:
                        this.showFilterList = toolsUtils.deepClone(FILTER_LIST)
                        break
                    case 1:
                        const item = list[0]
                        // type
                        if (item.id === 'type') {
                            if (item.values[0].id === 'common') {
                                this.showFilterList = []
                                break
                            }
                            this.showFilterList = [toolsUtils.deepClone(FILTER_LIST[1])]
                            break
                        }
                        // project
                        const fList = toolsUtils.deepClone(FILTER_LIST[0])
                        fList.children.splice(0, 1)
                        this.showFilterList = [fList]
                        break
                    default:
                        this.showFilterList = []
                }
            },
            // 搜索值改变
            onSearchChange (list) {
                this.filterSelectItem(list)
            },
            getTplIndexInSelected () {

            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
@import '@/scss/config.scss';
.export-container {
    position: relative;
    height: 340px;
    .search-wrapper {
        padding: 0 18px 0 20px;
    }
    .template-wrapper {
        float: left;
        padding: 20px 4px 20px 0;
        width: 557px;
        height: 100%;
        .template-list {
            padding: 0 14px 0 20px;
            height: 268px;
            overflow-y: auto;
            @include scrollbar;
        }
        .template-group {
            margin-bottom: 30px;
        }
        .search-list {
            padding-top: 40px;
        }
        .group-name {
            margin-bottom: 8px;
            font-size: 12px;
        }
    }
    .template-item {
        position: relative;
        display: inline-block;
        margin: 0 0 7px 10px;
        width: 252px;
        background: #dcdee5;
        border-radius: 2px;
        overflow: hidden;
        cursor: pointer;
        &:nth-child(2n + 1) {
            margin-left: 0;
        }
        .template-item-icon {
            float: left;
            width: 56px;
            height: 56px;
            line-height: 56px;
            background: #c4c6cc;
            font-size: 24px;
            color: #ffffff;
            text-align: center;
        }
        .template-item-name {
            color: #313238;
            word-break: break-all;
            @include multiLineEllipsis(14px, 2);
            &:after {
                background: #dcdee5
            }
        }
        .apply-permission-mask {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            text-align: center;
            .bk-button {
                margin-top: 12px;
            }
        }
        &:nth-child(2n) {
            margin-right: 0;
        }
        &.permission-disable {
            background: #f7f7f7;
            .template-item-icon {
                color: #dcdee5;
                background: #f7f7f7;
                border: 1px solid #dcdee5;
            }
            .item-name-box {
                border: 1px solid #dcdee5;
                border-left: none;
            }
            .template-item-name {
                color: #c4c6cc;
                &:after {
                    background: #f7f7f7;
                }
            }
            .apply-permission-mask {
                background: rgba(255, 255, 255, 0.6);
                text-align: center;
            }
            .bk-button {
                height: 32px;
                line-height: 30px;
            }
            &:hover .apply-permission-mask {
                display: block;
            }
        }
    }
    .item-name-box {
        display: table-cell;
        vertical-align: middle;
        margin-left: 56px;
        padding: 0 15px;
        height: 56px;
        width: 195px;
        font-size: 12px;
        border-radius: 0 2px 2px 0;
    }
    .template-item-selected {
        .template-item-icon {
            background: #666a7c;
        }
        .template-item-name, .item-name-box {
            background: #838799;
            color: #ffffff;
            &:after {
                background: #838799
            }
        }
    }
    .empty-template {
        padding-top: 40px;
    }
    .selected-wrapper {
        width: 292px;
        height: 100%;
        margin-left: 557px;
        padding-right: 4px;
        border-left:1px solid #dde4eb;
        .selected-area-title {
            padding: 28px 20px 22px;
            line-height: 1;
            font-size: 14px;
            font-weight: 600;
            color: #313238;
            .select-count {
                color: #3a84ff;
            }
        }
    }
    .selected-list {
        padding-top: 8px;
        height: 276px;
        overflow-y: auto;
        @include scrollbar;
        .selected-item {
            position: relative;
            margin: 0 0 10px 14px;
            width: 252px;
            height: 56px;
            background: #838799;
            border-radius: 2px;
            &:hover .selected-delete {
                display: inline-block;
            }
        }
        .selected-item-icon {
            float: left;
            width: 56px;
            height: 56px;
            line-height: 56px;
            background: #666a7c;
            border-radius: 2px;
            .selected-name {
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 24px;
                color: #ffffff;
            }
        }
        .selected-item-name {
            color: #ffffff;
            word-break: break-all;
            @include multiLineEllipsis(14px, 2);
            &:after {
                background: #838799
            }
        }
        .selected-delete {
            display: none;
            position: absolute;
            top: -7px;
            right: -7px;
            padding: 2px;
            color: #838799;
            background: #ffffff;
            border-radius: 50%;
            cursor: pointer;
        }
    }
    .template-checkbox {
        position: absolute;
        left: 20px;
        bottom: -42px;
    }
    .task-footer {
        position: absolute;
        right: 290px;
        bottom: -40px;
        .error-info {
            margin-right: 20px;
            font-size: 12px;
            color: #ea3636;
        }
    }
}
</style>
