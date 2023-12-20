/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="my-collection" data-test-id="home_form_myCollection" v-bkloading="{ isLoading: collectionBodyLoading, opacity: 1, zIndex: 100 }">
        <h3 class="panel-title">
            {{ $t('我的收藏') }}
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
            <span>{{ $t('常用流程到收藏夹，可作为你的流程管理快捷入口') }}</span>
        </panel-nodata>
        <select-create-task-dialog
            :create-task-item="createTaskItem"
            :is-create-task-dialog-show="isCreateTaskDialogShow"
            @cancel="onHideCreateTask">
        </select-create-task-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import PanelNodata from './PanelNodata.vue'
    import BaseCard from '@/components/common/base/BaseCard.vue'
    import SelectCreateTaskDialog from './SelectCreateTaskDialog.vue'
    import permission from '@/mixins/permission.js'
    import toolsUtils from '@/utils/tools.js'
    import { mapMutations, mapActions } from 'vuex'
    export default {
        name: 'MyCollection',
        components: {
            BaseCard,
            PanelNodata,
            SelectCreateTaskDialog
        },
        mixins: [permission],
        data () {
            return {
                createTaskItem: {},
                collectionList: [],
                collectionGrounpList: [],
                categorySwitchMap: {},
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
            let storageData = localStorage.getItem('myCollection')
            storageData = storageData ? JSON.parse(storageData) : {}
            Object.keys(storageData).forEach(key => {
                this.categorySwitchMap[key] = storageData[key]
            })
        },
        beforeDestroy () {
            window.removeEventListener('resize', this.onWindowResize, false)
        },
        methods: {
            ...mapActions([
                'changeDefaultProject',
                'deleteCollect',
                'loadCollectList'
            ]),
            ...mapMutations('project', [
                'setProjectId'
            ]),
            async initData () {
                try {
                    this.collectionBodyLoading = true
                    const res = await this.loadCollectList()
                    this.collectionList = res.data
                    this.collectionGrounpList = this.getGrounpList(res.data)
                    this.collectionBodyLoading = false
                } catch (e) {
                    console.log(e)
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
                        const method = collect.category === 'project' ? 'unshift' : 'push'
                        grounp[method]({
                            name: this.getCategoryChineseName(collect.category),
                            key: collect.category,
                            childrens: [collect]
                        })
                        names[method](collect.category)
                        this.$set(this.categorySwitchMap, collect.category, false)
                    }
                })
                return grounp
            },
            getCategoryChineseName (enType) {
                const categoryMap = {
                    'project': i18n.t('项目'),
                    'flow': i18n.t('项目流程'),
                    'common_flow': i18n.t('公共流程'),
                    'mini_app': i18n.t('轻应用'),
                    'periodic_task': i18n.t('周期任务')
                }
                return categoryMap[enType]
            },
            onSwitchCategory (key) {
                this.categorySwitchMap[key] = !this.categorySwitchMap[key]
                let storageData = localStorage.getItem('myCollection')
                storageData = storageData ? JSON.parse(storageData) : {}
                storageData[key] = this.categorySwitchMap[key]
                localStorage.setItem('myCollection', JSON.stringify(storageData))
            },
            // card 点击删除
            onDeleteCard (data) {
                this.$bkInfo({
                    title: i18n.t('确认删除收藏?'),
                    maskClose: false,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.onDeleteConfirm(data.id)
                    }
                })
            },
            // 确定删除
            async onDeleteConfirm (collectId) {
                this.deleteCollectLoading = true
                await this.deleteCollect(collectId)
                this.deleteCollectLoading = false
                this.initData()
            },
            // card 点击
            onCardClick (template) {
                if (this.getRourcePerm(template)) {
                    return this.checkForPermission(template)
                }
                window.reportInfo({
                    page: 'home',
                    zone: 'collectedCard',
                    event: 'click'
                })
                const type = template.category
                // 有权限执行
                const { project_id, id, name } = template.extra_info
                switch (type) {
                    case 'common_flow':
                        this.openSelectCreateTask(template)
                        break
                    case 'flow':
                        this.$router.push({
                            name: 'processHome',
                            params: { project_id },
                            query: { template_id: String(id) }
                        })
                        break
                    case 'periodic_task':
                        this.$router.push({
                            name: 'periodicTemplate',
                            params: { project_id },
                            query: { task_id: id }
                        })
                        break
                    case 'mini_app':
                        this.$router.push({
                            name: 'appMakerList',
                            params: { project_id },
                            query: { flowName: name }
                        })
                        break
                    case 'project':
                        this.setProjectId(id)
                        this.changeDefaultProject(id)
                        this.$router.push({
                            name: 'processHome',
                            params: { project_id: id }
                        })
                }
            },
            openSelectCreateTask (item) {
                this.isCreateTaskDialogShow = true
                this.createTaskItem = item
            },
            /**
             * 判断单个资源权限，这里只做了流程模板的权限校验
             */
            getRourcePerm (item) {
                if (item.category === 'flow') {
                    return !this.hasPermission(['flow_create_task'], item.auth_actions)
                } else if (item.category === 'project') {
                    return !this.hasPermission(['project_view'], item.auth_actions)
                }
                return false
            },
            /**
             * 申请对应权限
             */
            checkForPermission (item) {
                if (item.category === 'flow') {
                    item.name = item.extra_info.name
                    const { instance_id: id, name, extra_info: info } = item
                    const resourceData = {
                        flow: [{ id, name }],
                        project: [
                            {
                                id: info.project_id,
                                name: info.project_name
                            }
                        ]
                    }
                    this.applyForPermission(['flow_create_task'], item.auth_actions, resourceData)
                } else if (item.category === 'project') {
                    const resourceData = {
                        project: [{
                            id: item.extra_info.id,
                            name: item.extra_info.name
                        }]
                    }
                    this.applyForPermission(['project_view'], item.auth_actions, resourceData)
                }
            },
            onHideCreateTask () {
                this.isCreateTaskDialogShow = false
            },
            handlerWindowResize () {
                const cardList = document.querySelector('.my-collection .card-list')
                const cardItem = document.querySelector('.my-collection .card-list .card-item')
                if (
                    !this.collectionList
                    || this.collectionList.length === 0
                    || !cardList
                    || !cardItem) {
                    return
                }
                this.limit = Math.floor(cardList.offsetWidth / cardItem.offsetWidth)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
.my-collection {
    padding: 20px 24px 28px 24px;
    background: #ffffff;
    .panel-title {
        margin-top: 0;
        margin-bottom: 20px;
        color: #313238;
        font-size: 16px;
        font-weight: 600;
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
                border-radius: 2px;
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
