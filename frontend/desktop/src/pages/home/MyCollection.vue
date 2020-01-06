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
    <div class="my-collection" v-bkloading="{ isLoading: collectionBodyLoading, opacity: 1 }">
        <h3 class="panel-title">
            {{ i18n.title }}
            <span class="add-btn" @click="onAddCollection">{{ i18n.add }}</span>
        </h3>
        <div
            v-for="(grounp, index) in collectionGrounpList"
            :key="index"
            class="category-item">
            <h4 class="grounp-name">
                {{ grounp.name }}
                <span
                    v-if="grounp.childrens.length > limit"
                    :class="[
                        'switch-btn',
                        'common-icon-arrow-down',
                        { 'flip-icon': categorySwitchMap[grounp.key] }
                    ]"
                    @click.stop="onSwitchCategory(grounp.key)">
                </span>
            </h4>
            <ul
                :class="['card-list', { 'show-all': categorySwitchMap[grounp.key] }]">
                <base-card
                    v-for="(item, i) in grounp.childrens"
                    :key="i"
                    :data="item"
                    :set-name="item.extra_info.name"
                    :is-apply-permission="getRourcePerm(item)"
                    :show-delete="!getRourcePerm(item)"
                    @onCardClick="onCardClick"
                    @onDeleteCard="onDeleteCard">
                </base-card>
            </ul>
        </div>
        <panel-nodata v-if="!collectionGrounpList.length">
            <span class="link-text" @click="onAddCollection">{{ i18n.add }}</span>
            <span>{{ i18n.noDataDesc }}</span>
        </panel-nodata>
        <add-collection-dialog
            :collection-list="collectionList"
            :is-add-collection-dialog-show="isShowAdd"
            @onCloseDialog="onCloseDialog">
        </add-collection-dialog>
        <select-create-task-dialog
            :tpl-resource="collectionResource.common_flow"
            :tpl-operations="tplOperations"
            :create-task-item="createTaskItem"
            :is-create-task-dialog-show="isCreateTaskDialogShow"
            @cancel="onHideCreateTask">
        </select-create-task-dialog>
        <bk-dialog
            width="400"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="i18n.delete"
            :value="isDeleteDialogShow"
            @confirm="onDeleteConfirm"
            @cancel="onDeleteCancel">
            <div style="padding:30px" v-bkloading="{ isLoading: deleteCollectLoading, opacity: 1 }">
                {{i18n.deleteTips}}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import PanelNodata from './PanelNodata.vue'
    import BaseCard from '@/components/common/base/BaseCard.vue'
    import AddCollectionDialog from './AddCollectionDialog.vue'
    import SelectCreateTaskDialog from './SelectCreateTaskDialog.vue'
    import permission from '@/mixins/permission.js'
    import toolsUtils from '@/utils/tools.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { mapActions } from 'vuex'
    export default {
        name: 'MyCollection',
        components: {
            BaseCard,
            PanelNodata,
            AddCollectionDialog,
            SelectCreateTaskDialog
        },
        mixins: [permission],
        data () {
            return {
                i18n: {
                    title: gettext('我的收藏'),
                    add: gettext('添加'),
                    delete: gettext('删除'),
                    deleteTips: gettext('确认删除收藏？'),
                    noDataDesc: gettext('常用流程到收藏夹，可作为你的流程管理快捷入口')
                },
                createTaskItem: '',
                tplOperations: [],
                collectionResource: {},
                collectionList: [],
                collectionGrounpList: [],
                categorySwitchMap: {},
                isShowAdd: false, // 显示添加收藏
                isDeleteDialogShow: false, // 显示确认删除
                deleteCollectLoading: false, // 确认删除按钮 loading
                isCreateTaskDialogShow: false, // 显示创建任务 dialog
                collectionBodyLoading: false, // 收藏 body
                limit: 4
            }
        },
        created () {
            this.onWindowResize = toolsUtils.debounce(this.handlerWindowResize, 300)
        },
        async mounted () {
            window.addEventListener('resize', this.onWindowResize, false)
            await this.initData()
            this.handlerWindowResize()
        },
        beforeDestroy () {
            window.removeEventListener('resize', this.onWindowResize, false)
        },
        methods: {
            ...mapActions('template/', [
                'deleteCollect',
                'getCollectList'
            ]),
            async initData () {
                try {
                    this.collectionBodyLoading = true
                    const res = await this.getCollectList()
                    if (res.objects && res.objects.length > 0) {
                        this.tplOperations = res.meta.auth_operations
                        this.collectionResource = res.meta.auth_resource
                    }
                    this.collectionList = res.objects
                    this.collectionGrounpList = this.getGrounpList(res.objects)
                    this.collectionBodyLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            getLimit () {
                return document.body.clientWidth > 1920 ? 6 : 4
            },
            getGrounpList (list) {
                const grounp = []
                const names = []
                list.forEach(collect => {
                    const index = names.indexOf(collect.category)
                    if (index > -1) {
                        grounp[index].childrens.push(collect)
                    } else {
                        grounp.push({
                            name: this.getCategoryChineseName(collect.category),
                            key: collect.category,
                            childrens: [collect]
                        })
                        names.push(collect.category)
                        this.$set(this.categorySwitchMap, collect.category, false)
                    }
                })
                return grounp
            },
            getCategoryChineseName (enType) {
                const categoryMap = {
                    'flow': gettext('项目流程'),
                    'common_flow': gettext('公共流程'),
                    'mini_app': gettext('轻应用'),
                    'periodic_task': gettext('周期任务')
                }
                return categoryMap[enType]
            },
            onSwitchCategory (key) {
                this.categorySwitchMap[key] = !this.categorySwitchMap[key]
            },
            // 打开添加收藏
            onAddCollection () {
                this.isShowAdd = true
            },
            // 关闭添加收藏
            onCloseDialog (save) {
                if (save) {
                    this.initData()
                }
                this.isShowAdd = false
            },
            // card 点击删除
            onDeleteCard (data) {
                this.isDeleteDialogShow = true
                this.deleteCollectId = data.id
            },
            // 确定删除
            async onDeleteConfirm () {
                this.deleteCollectLoading = true
                await this.deleteCollect(this.deleteCollectId)
                this.deleteCollectLoading = false
                this.isDeleteDialogShow = false
                this.initData()
            },
            // 取消删除
            onDeleteCancel () {
                this.isDeleteDialogShow = false
            },
            // card 点击
            onCardClick (template) {
                if (this.getRourcePerm(template)) {
                    return this.checkForPermission(template)
                }
                const type = template.category
                // 有权限执行
                const { project_id, template_id, app_id, name } = template.extra_info
                switch (type) {
                    case 'common_flow':
                        this.openSelectCreateTask(template)
                        break
                    case 'flow':
                        this.$router.push({
                            name: 'taskStep',
                            params: { step: 'selectnode', project_id },
                            query: { template_id }
                        })
                        break
                    case 'periodic_task':
                        this.$router.push({
                            name: 'periodicTemplate',
                            params: { project_id },
                            query: { q: name } // q 表示筛选 Id 值
                        })
                        break
                    case 'mini_app':
                        const { href } = this.$router.resolve({
                            name: 'appmakerTaskCreate',
                            params: { step: 'selectnode', app_id, project_id },
                            query: { template_id }
                        })
                        window.open(href, '_blank')
                }
            },
            openSelectCreateTask (item) {
                this.isCreateTaskDialogShow = true
                this.createTaskItem = item
            },
            /**
             * 判断单个资源权限
             */
            getRourcePerm (item) {
                if (item.category === 'flow') {
                    return !this.hasPermission(['create_task'], item.auth_actions, this.tplOperations)
                }
                return false
            },
            /**
             * 申请对应权限
             */
            checkForPermission (item) {
                if (item.category === 'flow') {
                    item.name = item.extra_info.name
                    this.applyForPermission(['create_task'], item, this.tplOperations, this.collectionResource.flow)
                }
            },
            onHideCreateTask () {
                this.isCreateTaskDialogShow = false
            },
            handlerWindowResize () {
                if (!this.collectionList || this.collectionList.length === 0) {
                    return
                }
                const cardView = document.querySelector('.my-collection .card-list').offsetWidth
                const cardItemW = document.querySelector('.common-used .card-list .card-item').offsetWidth
                this.limit = Math.floor(cardView / cardItemW)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
.my-collection {
    margin-top: 20px;
    padding: 20px 24px 28px 24px;
    background: #ffffff;
    .panel-title {
        margin-top: 0;
        margin-bottom: 20px;
        color: #313238;
        font-size: 16px;
        font-weight: 600;
        .add-btn {
            float: right;
            font-size: 12px;
            color: #3a84ff;
            font-weight: normal;
            cursor: pointer;
        }
    }
    .category-item {
        .grounp-name {
            margin: 10px 0;
            font-size: 12px;
            color: #979ba5;
            font-weight: normal;
            height: 18px;
            line-height: 18px;
            .switch-btn {
                float: right;
                cursor: pointer;
                transition: all 0.3s;
                &.flip-icon {
                    transform: rotate(-180deg);
                }
                &:hover {
                    color: #63656e;
                }
            }
        }
        .card-list {
            clear: both;
            overflow: hidden;
            margin-top: -20px;
            max-height: 82px;
            padding-right: 6px;
            &.show-all {
                max-height: none;
            }
            .card-item {
                display: inline-block;
                margin-right: 0;
                @media screen and (max-width: 1560px) {
                    &:not(:nth-child(4n)) {
                        margin-right: 16px;
                    }
                    width: calc( (100% - 48px) / 4 );
                }
                @media screen and (min-width: 1561px) and (max-width: 1919px) {
                    &:not(:nth-child(5n)) {
                        margin-right: 16px;
                    }
                    width: calc( (100% - 64px) / 5 );
                }
                @media screen and (min-width: 1920px) {
                    &:not(:nth-child(6n)) {
                        margin-right: 16px;
                    }
                   width: calc( (100% - 80px) / 6 );
                }
            }
        }
    }
    .link-text {
        color: #3a84ff;
        cursor: pointer;
    }
}
</style>
