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
    <div class="card-wrapper">
        <div class="card-basic">
            <div class="logo" @click="onGotoAppMaker">
                <div v-if="isShowDefaultLogo" class="default-logo">
                    <img class="default-icon" :src="require(`@/assets/images/appmaker-default-icon-1.png`)" alt="default-icon-1">
                </div>
                <div v-else>
                    <img class="logo-pic" :src="appData.logo_url" @error="useDefaultLogo" />
                </div>
            </div>
            <div class="app-name-wrap">
                <a
                    class="app-name"
                    :title="appData.name"
                    @click.self="onGotoAppMaker">
                    {{appData.name}}
                </a>
            </div>
            <div class="card-operation">
                <span
                    :class="['common-icon-box-pen', 'operate-btn', {
                        'permission-disable': !hasPermission(['edit'], appData.auth_actions, appOperations)
                    }]"
                    :title="$t('修改轻应用')"
                    v-cursor="{ active: !hasPermission(['edit'], appData.auth_actions, appOperations) }"
                    @click.stop="onCardEdit">
                </span>
                <router-link
                    class="common-icon-clock-reload operate-btn"
                    :title="$t('执行历史')"
                    :to="getExecuteHistoryUrl(appData.template_id)">
                </router-link>
                <bk-popover
                    theme="light"
                    placement="bottom-start"
                    ext-cls="common-dropdown-btn-popver"
                    :z-index="2000"
                    :distance="0"
                    :arrow="false"
                    :tippy-options="{ boundary: 'window', duration: [0, 0], appendTo: 'parent' }">
                    <span class="common-icon-circle-ellipsis operate-btn"></span>
                    <ul class="operate-list" slot="content">
                        <li
                            v-cursor="{ active: !hasPermission(['view'], appData.auth_actions, appOperations) }"
                            href="javascript:void(0);"
                            :class="{
                                'opt-btn': true,
                                'disable': collectingId === appData.id || collectedLoading,
                                'text-permission-disable': !hasPermission(['view'], appData.auth_actions, appOperations)
                            }"
                            @click="onCollectAppMaker(appData, $event)">
                            {{ isCollected(appData.id) ? $t('取消收藏') : $t('收藏') }}
                        </li>
                        <li
                            :class="{
                                'opt-btn': true,
                                'text-permission-disable': !hasPermission(['delete'], appData.auth_actions, appOperations)
                            }"
                            v-cursor="{ active: !hasPermission(['delete'], appData.auth_actions, appOperations) }"
                            @click="onCardDelete">
                            {{$t('删除')}}
                        </li>
                    </ul>
                </bk-popover>
            </div>
        </div>
        <div class="card-particular">
            <div class="app-detail">
                <div class="app-template">{{$t('流程模板')}}
                    <p>{{appData.template_name}}</p>
                </div>
                <div class="editor-name">{{$t('更新人')}}
                    <p>{{appData.editor_name}}</p>
                </div>
                <div class="edit-time">{{$t('更新时间')}}
                    <p>{{appData.edit_time}}</p>
                </div>
            </div>
            <div class="app-synopsis">{{$t('应用简介')}}
                <p class="synopsis-content">{{appData.desc || '--'}}</p>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'
    import { mapActions } from 'vuex'

    export default {
        name: 'AppCard',
        mixins: [permission],
        props: {
            appData: Object,
            project_id: [Number, String],
            appResource: Object,
            appOperations: Array,
            collectedLoading: Boolean,
            collectedList: Array
        },
        data () {
            return {
                isLogoLoadingError: false,
                isShowEdit: false,
                mouseAccess: true,
                collectingId: '', // 正在被收藏/取消收藏的轻应用id
                collectionList: []
            }
        },
        computed: {
            isShowDefaultLogo () {
                return this.isLogoLoadingError || !this.appData.logo_url
            }
        },
        methods: {
            ...mapActions([
                'addToCollectList',
                'deleteCollect'
            ]),
            useDefaultLogo () {
                this.isLogoLoadingError = true
            },
            /**
             * 单个轻应用操作项点击时校验
             * @params {Array} required 需要的权限
             * @params {Object} app 模板数据对象
             * @params {Object} event 事件对象
             */
            onAppMakerPermissonCheck (required, app, event) {
                this.applyForPermission(required, app, this.appOperations, this.appResource)
                event.preventDefault()
            },
            onShowOperation () {
                this.isShowEdit = true
            },
            onHideOperation () {
                this.isShowEdit = false
            },
            onCardEdit () {
                if (!this.hasPermission(['edit'], this.appData.auth_actions, this.appOperations)) {
                    this.onAppMakerPermissonCheck(['edit'], this.appData, event)
                    return
                }
                this.$emit('onCardEdit', this.appData)
            },
            onCardDelete () {
                if (!this.hasPermission(['delete'], this.appData.auth_actions, this.appOperations)) {
                    this.onAppMakerPermissonCheck(['delete'], this.appData, event)
                    return
                }
                this.$emit('onCardDelete', this.appData)
            },
            onGotoAppMaker () {
                if (!this.hasPermission(['view'], this.appData.auth_actions, this.appOperations)) {
                    this.onAppMakerPermissonCheck(['view'], this.appData, event)
                    return
                }
                if (self === top) {
                    window.open(this.appData.link, '_blank')
                } else {
                    window.PAAS_API.open_other_app(this.appData.code, this.appData.link)
                }
            },
            // 查询执行记录
            getExecuteHistoryUrl (id) {
                return {
                    name: 'taskList',
                    params: { project_id: this.project_id },
                    query: { template_id: id, create_method: 'app_maker' }
                }
            },
            // 添加/取消收藏模板
            async onCollectAppMaker (data, event) {
                if (!this.hasPermission(['delete'], this.appData.auth_actions, this.appOperations)) {
                    this.onAppMakerPermissonCheck(['view'], this.appData, event)
                    return
                }
                if (typeof this.collectingId === 'number') {
                    return
                }
                try {
                    this.collectingId = data.id
                    if (!this.isCollected(data.id)) { // add
                        const res = await this.addToCollectList([{
                            extra_info: {
                                app_id: data.id,
                                project_id: data.project.id,
                                template_id: data.template_id,
                                name: data.name,
                                id: data.id
                            },
                            category: 'mini_app'
                        }])
                        if (res.objects.length) {
                            this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        }
                    } else { // cancel
                        const delId = this.collectedList.find(m => m.extra_info.id === data.id && m.category === 'mini_app').id
                        await this.deleteCollect(delId)
                        this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                    }
                    this.$emit('getCollectList')
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.collectingId = ''
                }
            },
            // 判断是否已在收藏列表
            isCollected (id) {
                return !!this.collectedList.find(m => m.extra_info.id === id && m.category === 'mini_app')
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.card-wrapper {
    position: relative;
    min-width: 345px;
    height: 184px;
    color: #63656e;
    background: $whiteDefault;
    border: 1px solid $commonBorderColor;
    border-radius: 2px;
}
.card-basic {
    float: left;
    position: relative;
    width: 40%;
    height: 100%;
    padding: 20px 15px;
    border-right: 1px solid $commonBorderColor;
    &:hover {
        background: #f0f1f5;
        .card-operation {
            bottom: 10px;
            z-index: 1;
            opacity: 1;
            visibility: visible;
        }
    }
    .logo {
        width: 60px;
        height: 60px;
        margin: 0 auto;
        cursor: pointer;
        .logo-pic {
            width: 60px;
            height: 60px;
            border-radius: 6px;
        }
    }
    .default-logo {
        width: 100%;
        height: 100%;
        text-align: center;
        border-radius: 6px;
        .default-icon {
            margin-top: 10px;
            max-height: 55px;
        }
    }
    .app-name-wrap {
        margin: 10px 0;
        height: 40px;
        .app-name {
            display: block;
            display: -webkit-box;
            font-size: 14px;
            font-weight: bold;
            color: #63656e;
            word-break: break-all;
            cursor: pointer;
            text-align: center;
            overflow : hidden;
            text-overflow: ellipsis;
            word-break: break-all;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            &:hover {
                color: $blueDefault;
            }
        }
    }
}
.card-operation {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    font-size: 24px;
    color: #979ba5;
    text-align: center;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    .operate-btn {
        padding: 5px;
        font-size: 14px;
        color: #ffffff;
        background: #d8dadc;
        border-radius: 2px;
        cursor: pointer;
        &:not(.permission-disable):hover {
            background: #979ba5;
        }
    }
    .operate-list {
        font-size: 12px;
        li {
            padding: 0 12px;
            min-width: 80px;
            height: 32px;
            line-height: 32px;
            color: #63656e;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
                background: #ebf4ff;
            }
            &.disable {
                color: #dcdee5;
            }
        }
    }
}
.edit-box {
    width: 96px;
    height: 84px;
    background: #fff;
    box-shadow: 0px 2px 4px 0px rgba(0,0,0,0.2);
    border-radius: 2px;
    &:hover {
        z-index: 10;
    }
    .edit-operation {
        width: 96px;
        height: 42px;
        color: #63656e;
        font-size: 12px;
        font-weight: 400;
        line-height: 42px;
        text-align: center;
        background: #fff;
        &:hover {
            color: #3a84ff;
            background: #ebf4ff;
        }
    }
}
.edit-box>li>a {
    display: block;
    color: #fff;
    height: 42px;
    &:hover {
        background: #63656e;
    }
}
.card-particular {
    float: left;
    width: 60%;
    height: 100%;
    background: #f7f9fa;
    .app-detail {
        padding: 20px;
        font-size: 12px;
        & > p {
            width: 220px;
            color: $greyDark;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
    }
    .app-template, .editor-name, .edit-time {
        margin-bottom: 10px;
        font-weight: bold;
        p {
            margin-top: 3px;
            font-weight: 400;
        }
    }
    &:hover {
        .app-synopsis {
            display: block;
        }
    }
    .app-synopsis {
        display: none;
        position: absolute;
        bottom: 0px;
        height: 100%;
        width: 60%;
        background: #f7f9fa;
        font-weight: bold;
        font-size: 12px;
        padding: 20px;
        p {
            margin-top: 3px;
            font-weight: 400;
        }
    }
    .synopsis-content {
        height: 130px;
        width: 100%;
        white-space: pre-line;
        word-wrap:break-word;
        overflow-y: auto;
    }
}
</style>
