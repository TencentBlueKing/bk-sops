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
        <h3 class="panel-title">{{ i18n.title }}</h3>
        <ul v-if="collectionList.length" class="card-list">
            <base-card
                v-for="(item, index) in collectionList"
                :key="index"
                :data="item"
                :set-name="item.extra_info.name"
                :is-apply-permission="getRourcePerm(item)"
                @onCardClick="onCardClick"
                @onDeleteCard="onDeleteCard">
            </base-card>
            <li class="add-collection" @click="onAddCollection">+</li>
        </ul>
        <panel-nodata v-else>
            <span class="link-text" @click="onAddCollection">{{ i18n.add }}</span>
            <span>{{ i18n.noDataDesc }}</span>
        </panel-nodata>
        <add-collection-dialog
            :is-add-collection-dialog-show="isShowAdd"
            @onCloseDialog="onCloseDialog">
        </add-collection-dialog>
        <select-create-task-dialog
            :create-task-template-id="createTaskTemplateId"
            :is-create-task-dialog-show="isCreateTaskDialogShow">
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
                createTaskTemplateId: '',
                tplOperations: [],
                collectionList: [],
                isShowAdd: false, // 显示添加收藏
                isDeleteDialogShow: false, // 显示确认删除
                deleteCollectLoading: false, // 确认删除按钮 loading
                isCreateTaskDialogShow: false, // 显示创建任务 dialog
                collectionBodyLoading: false // 收藏 body
            }
        },
        created () {
        },
        mounted () {
            this.initData()
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
                    this.tplOperations = res.meta.auth_operations
                    this.collectionResource = res.meta.auth_resource
                    this.collectionList = res.objects
                    this.collectionBodyLoading = false
                } catch (e) {
                    errorHandler(e, this)
                }
            },
            // 打开添加收藏
            onAddCollection () {
                this.isShowAdd = true
            },
            // 关闭添加收藏
            onCloseDialog () {
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
                    case 'common':
                        this.openSelectCreateTask(template_id)
                        break
                    case 'process':
                        this.$router.push({
                            name: 'taskStep',
                            params: { step: 'selectnode', project_id },
                            query: { template_id }
                        })
                        break
                    case 'periodic':
                        this.$router.push({
                            name: 'periodicTemplate',
                            params: { project_id },
                            query: { q: name } // q 表示筛选 Id 值
                        })
                        break
                    case 'app_maker':
                        const { href } = this.$router.resolve({
                            name: 'appmakerTaskCreate',
                            params: { step: 'selectnode', app_id, project_id },
                            query: { template_id }
                        })
                        window.open(href, '_blank')
                }
            },
            openSelectCreateTask (templateId) {
                this.isCreateTaskDialogShow = true
                this.createTaskTemplateId = templateId
            },
            /**
             * 判断单个资源权限
             */
            getRourcePerm (item) {
                if (item.category === 'process') {
                    return !this.hasPermission(['create_task', 'create_template'], item.auth_actions, this.tplOperations)
                }
                return false
            },
            /**
             * 申请对应权限
             */
            checkForPermission (item) {
                if (item.category === 'process') {
                    this.applyForPermission(['create_task', 'create_template'], item, this.tplOperations, this.collectionResource)
                }
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
        color: #313238;
        font-size: 16px;
        font-weight: 600;
    }
    .card-list {
        display: flex;
        flex-wrap: wrap;
        overflow: hidden;
        margin-top: -20px;
    }
    .add-collection {
        margin-top: 20px;
        width: 278px;
        height: 60px;
        line-height: 60px;
        font-size: 18px;
        color: #c4c6cc;
        text-align: center;
        background: #fcfcfc;
        cursor: pointer;
        border: 1px solid #f0f1f5;
        &:hover {
            background: #e1ecff;
            color: #3a84ff;
        }
    }
    .link-text {
        color: #3a84ff;
        cursor: pointer;
    }
}
</style>
