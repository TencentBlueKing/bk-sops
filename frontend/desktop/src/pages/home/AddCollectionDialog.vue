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
        <div class="export-container">
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
                                                'permission-disable': !hasPermission(['view'], template.auth_actions, tplOperations)
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
        <DialogLoadingBtn
            slot="footer"
            :dialog-footer-data="dialogFooterData"
            @onConfirm="onConfirm"
            @onCancel="onCancel">
        </DialogLoadingBtn>
    </bk-dialog>
</template>
<script>
    import '@/utils/i18n.js'
    import toolsUtils from '@/utils/tools.js'
    import { mapGetters, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import permission from '@/mixins/permission.js'
    import DialogLoadingBtn from '@/components/common/base/DialogLoadingBtn.vue'
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
                    id: 'periodic'
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
            NoData,
            DialogLoadingBtn
        },
        mixins: [permission],
        props: ['isAddCollectionDialogShow'],
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
                tplOperations: [],
                tplResource: {},
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
        watch: {
            isAddCollectionDialogShow (val) {
                if (val) {
                    this.getData()
                }
            }
        },
        methods: {
            ...mapActions('template/', [
                'loadCollectList',
                'collectSelect'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions('appmaker', [
                'loadAppmaker'
            ]),
            ...mapActions('periodic/', [
                'loadPeriodicList'
            ]),
            async getData () {
                this.panelList = []
                try {
                    let panelList = []
                    let reqType = ''
                    let searchStr = ''
                    let projectId
                    this.searchValue.forEach(value => {
                        if (value.id === 'type') {
                            reqType = value.values[0].id
                        } else if (value.id === 'project') {
                            projectId = value.values[0].id
                        } else {
                            searchStr += value.id
                        }
                    })
                    if (reqType !== 'common' && !projectId) {
                        return false
                    }
                    this.collectionPending = true
                    switch (reqType) {
                        case 'common':
                            panelList = await this.getTemplateList(1, searchStr)
                            break
                        case 'process':
                            panelList = await this.getTemplateList(false, searchStr, projectId)
                            break
                        case 'periodic':
                            panelList = await this.getPeriodicList(projectId, searchStr)
                            break
                        case 'app_maker':
                            panelList = await this.getAppMakerList(projectId, searchStr)
                            break
                        default:
                            panelList = []
                    }
                    this.panelList = this.getGroupData(panelList, reqType)
                    this.collectionPending = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            /**
             * 获取分组后的数组
             * @param {Boolean}  common 公共流程
             * @param {Number}  projectId 业务 Id
             * @param {String}  searchStr 搜索值
             */
            async getTemplateList (common, searchStr, projectId) {
                const data = await this.loadTemplateList({
                    common: common || undefined,
                    project__id: projectId || undefined,
                    pipeline_template__name__contains: searchStr || undefined
                })
                this.tplOperations = data.meta.auth_operations
                this.tplResource = data.meta.auth_resource
                return data.objects || []
            },
            async getAppMakerList (projectId, searchStr) {
                const data = await this.loadAppmaker({
                    project__id: projectId,
                    q: searchStr || undefined
                })
                return data.objects || []
            },
            async getPeriodicList (projectId, searchStr) {
                const data = await this.loadPeriodicList({
                    project__id: projectId,
                    task__name__contains: searchStr || undefined
                })
                return data.objects || []
            },
            // 分组
            getGroupData (list, type) {
                const categorys = []
                const group = []
                list.forEach(m => {
                    m.collectType = type
                    const index = categorys.indexOf(m.category)
                    if (index !== -1) {
                        group[index].children.push(m)
                    } else {
                        categorys.push(m.category)
                        group.push({
                            name: m.category,
                            children: [m]
                        })
                    }
                })
                return group
            },
            // 获取 icon
            getTemplateIcon (template) {
                return template.name.trim().substr(0, 1).toUpperCase()
            },
            // 选择收藏
            onSelectTemplate (template) {
                if (this.hasPermission(['view'], template.auth_actions, this.tplOperations)) {
                    this.selectError = false
                    const tplIndex = this.getTplIndexInSelected(template)
                    if (tplIndex > -1) {
                        this.selectedList.splice(tplIndex, 1)
                    } else {
                        this.selectedList.push(template)
                    }
                } else {
                    this.applyForPermission(['view'], template, this.tplOperations, this.tplResource)
                }
            },
            // 取消选中
            deleteTemplate (template) {
                const tplIndex = this.getTplIndexInSelected(template)
                this.selectedList.splice(tplIndex, 1)
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
                this.getData()
            },
            getTplIndexInSelected (template) {
                return this.selectedList.findIndex(item => item.id === template.id)
            },
            async onConfirm () {
                if (!this.selectedList.length) {
                    this.selectError = true
                    return false
                }
                this.dialogFooterData[0].loading = true
                const project = this.searchValue.find(m => m.id === 'project')
                let projectId
                if (project) {
                    projectId = project.values[0].id
                }
                const saveList = this.selectedList.map(template => {
                    const extra_info = this.getExtraInfo(template, template.collectType, projectId)
                    const saveCategoryMap = {
                        'process': 'flow',
                        'common': 'common_flow',
                        'periodic': 'periodic_task',
                        'app_maker': 'mini_app'
                    }
                    return {
                        extra_info,
                        category: saveCategoryMap[template.collectType]
                    }
                })
                try {
                    const res = await this.collectSelect(saveList)
                    this.dialogFooterData[0].loading = false
                    if (res.objects) {
                        this.$bkMessage({
                            message: gettext('保存成功'),
                            theme: 'success'
                        })
                        this.$emit('onCloseDialog', true)
                    } else {
                        errorHandler(res, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            // 保存参数
            getExtraInfo (template, type, projectId) {
                let extraInfo = {}
                switch (type) {
                    case 'common':
                        extraInfo = {
                            template_id: template.template_id,
                            name: template.name,
                            id: template.id
                        }
                        break
                    case 'process':
                        extraInfo = {
                            project_id: projectId,
                            template_id: template.template_id,
                            template_source: template.template_source,
                            name: template.name,
                            id: template.id
                        }
                        break
                    case 'periodic':
                        extraInfo = {
                            project_id: projectId,
                            template_id: template.template_id,
                            name: template.name,
                            id: template.id
                        }
                        break
                    case 'app_maker':
                        extraInfo = {
                            app_id: template.id,
                            project_id: projectId,
                            template_id: template.template_id,
                            name: template.name,
                            id: template.id
                        }
                }
                return extraInfo
            },
            onCancel () {
                this.$emit('onCloseDialog')
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
        padding-top: 104px;
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
