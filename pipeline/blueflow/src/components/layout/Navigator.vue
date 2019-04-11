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
    <header>
        <router-link v-if="userType === 'maintainer' && view_mode === 'app'" to="/" @click.native="onGoToPath(businessHomeRoute)">
            <img :src="logo" class="logo"/>
        </router-link>
        <img v-else :src="logo" class="logo"/>
        <nav>
            <div class="navigator" v-if="!appmakerDataLoading">
                <template v-for="route in routeList">
                    <div
                        v-if="route.children && route.children.length"
                        :key="route.key"
                        :class="['nav-item', { 'active': isNavActived(route)}]">
                        <span>{{route.name}}</span>
                        <div class="sub-nav">
                            <router-link
                                v-for="subRoute in route.children"
                                tag="a"
                                :key="subRoute.key"
                                :class="['sub-nav-item', {'selected': isSubNavActived(subRoute)}]"
                                :to="getPath(subRoute)"
                                @click.native="onGoToPath(subRoute)">
                                {{subRoute.name}}
                            </router-link>
                        </div>
                    </div>
                    <router-link
                        v-else
                        tag="a"
                        :key="route.key"
                        :class="['nav-item', { 'active': isNavActived(route)}]"
                        :to="getPath(route)"
                        @click.native="onGoToPath(route)">
                        {{route.name}}
                    </router-link>
                </template>
            </div>
        </nav>
        <div class="header-right clearfix">
            <BizSelector v-if="showHeaderRight" :disabled="disabled"></BizSelector>
            <div class="help-doc">
                <a
                    class="common-icon-dark-circle-question"
                    href="http://docs.bk.tencent.com/product_white_paper/gcloud/"
                    target="_blank">
                </a>
            </div>
            <div class="user-avatar">
                <span
                    class="common-icon-dark-circle-avatar"
                    v-bktooltips="{
                        content: username,
                        placement: 'bottom-left',
                        theme: 'light',
                        zIndex: 1001
                    }">
                </span>
            </div>
        </div>
    </header>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import { setAtomConfigApiUrls } from '@/config/setting.js'
import BizSelector from './BizSelector.vue'

const ROUTE_LIST = {
    // 职能化中心导航
    functor_router_list: [
        {
            key: 'function',
            path: '/function/home/',
            name: gettext('职能化中心')
        }
    ],
    // 职能化中心导航
    auditor_router_list: [
        {
            key: 'audit',
            path: '/audit/home/',
            name: gettext('审计中心')
        }
    ],
    // 通用导航
    maintainer_router_list: [
        {
            key: 'template',
            name: gettext('流程模板'),
            children: [
                {
                    key: 'template',
                    name: gettext('业务流程'),
                    path: '/template/home/'
                },
                {
                    key: 'commonTemplate',
                    name: gettext('公共流程'),
                    path: '/template/home/',
                    query: {common: 1, common_template: 'common'}
                }
            ]
        },
        {
            key: 'periodic',
            path: '/periodic/home/',
            name: gettext('周期任务')
        },
        {
            key: 'taskflow',
            path: '/taskflow/home/',
            name: gettext('任务记录')
        },
        {
            key: 'config',
            path: '/config/home/',
            name: gettext('业务配置')
        },
        {
            key: 'appmaker',
            path: '/appmaker/home/',
            name: gettext('轻应用')
        },
        {
            key: 'administrator',
            name: gettext('管理员入口'),
            children: [
                {
                    key: 'statistics',
                    name: gettext('运营数据'),
                    path: '/statistics/template/'
                },
                {
                    key: 'common',
                    name: gettext('公共流程'),
                    path: '/template/home/',
                    query: {common: 1}
                }
            ]
        }
    ]
}

export default {
    inject: ['reload'],
    name: 'Navigator',
    components: {
        BizSelector
    },
    props: ['appmakerDataLoading'],
    data () {
        return {
            subNavKey: '',
            logo: require('../../assets/images/logo/' + gettext('logo-zh') + '.svg'),
            i18n: {
                help: gettext("帮助文档")
            },
            businessHomeRoute: {
                key: 'business',
                path: '/business/home/'
            }
        }
    },
    computed: {
        ...mapState({
            site_url: state => state.site_url,
            username: state => state.username,
            userType: state => state.userType,
            cc_id: state => state.cc_id,
            app_id: state => state.app_id,
            view_mode: state => state.view_mode,
            bizList: state => state.bizList,
            templateId: state => state.templateId,
            notFoundPage: state => state.notFoundPage,
            isSuperUser: state => state.isSuperUser
        }),
        showHeaderRight () {
            return this.userType === 'maintainer' && this.view_mode !== 'appmaker' && this.bizList.length
        },
        routeList () {
            if (this.view_mode === 'appmaker') {
                return [
                    {
                        key: 'appmakerTaskCreate',
                        path: `/appmaker/${this.app_id}/newtask/${this.cc_id}/selectnode`,
                        query: {template_id: this.template_id},
                        name: gettext('新建任务')
                    },
                    {
                        key: 'appmakerTaskList',
                        path: `/appmaker/${this.app_id}/task_home/`,
                        name: gettext('任务记录')
                    }
                ]
            } else {
                let routes = ROUTE_LIST[`${this.userType}_router_list`]

                // 非管理员用户去掉管理员入口
                if (!this.isSuperUser) {
                    routes = routes.filter(item => item.key !== 'administrator')
                }
                return routes
            }
        },
        disabled () {
            const route = this.$route
            if (
                route.path.indexOf('/statistics/') > -1 ||
                route.query &&
                route.query.common &&
                !route.query.common_template &&
                route.name !== 'templateStep' &&
                route.name !== 'taskList'
            ) {
                return true
            }
            return false
        }
    },
    mounted () {
        this.initHome()
    },
    methods: {
        initHome () {
            if (this.userType === 'maintainer' && this.view_mode !== 'appmaker') {
                this.getBizList()
            }
        },
        ...mapActions([
            'getBizList',
            'changeDefaultBiz'
        ]),
        ...mapMutations([
            'setBizId'
        ]),
        isNavActived (route) {
            const key = route.key

            // 轻应用打开
            if (this.view_mode === 'appmaker') {
                if (this.$route.name === 'appmakerTaskExecute' || this.$route.name === 'appmakerTaskHome') {
                    return key === 'appmakerTaskList'
                } else {
                    return key === 'appmakerTaskCreate'
                }
            }

            // 职能化中心、审计中心打开
            if (this.userType === 'functor') {
                return key === 'function'
            } else if (this.userType === 'auditor') {
                return key === 'audit'
            }
            // 二级导航被选中
            if (route.children && route.children.length) {
                return route.children.some(item => {
                    return this.matchPathResult(item.key)
                })
            }

            return this.matchPathResult(key)
        },
        isSubNavActived (route) {
            return this.matchPathResult(route.key)
        },
        matchPathResult (key) {
            if (this.$route.query !== undefined && Object.keys(this.$route.query).length !== 0 && this.$route.query.common) {
                if (this.$route.query.common_template || this.$route.name === 'templateStep') {
                    return key === 'commonTemplate'
                } else if (this.$route.name !== 'taskList'){
                    return key === 'common'
                }
            }
            return new RegExp('^\/' + key).test(this.$route.path)
        },
        getPath (route) {
            /** 404 页面时，导航统一跳转到首页 */
            if (this.notFoundPage) {
                if (['functor', 'auditor'].indexOf(this.userType) === -1
                    && this.view_mode !== 'appmaker'
                ) {
                    return '/'
                }
                
            }

            let path
            if (route.key === 'appmakerTaskCreate') {
                path = `${route.path}?template_id=${this.templateId}`
            } else if (this.userType !== 'maintainer' || route.key === 'statistics') {
                path = `${route.path}`
            } else {
                path =  {path: `${route.path}${this.cc_id}/`, query: route.query}
            }
            return path
        },
        onGoToPath (route) {
            let path = this.getPath(route)
            // 点击当前导航刷新页面
            if (path === this.$route.path || path.path === this.$route.path) {
                this.refreshCurrentPage()
            }
            return
        },
        onClickSubNav (route) {
            this.onGoToPath(route)
        },
        refreshCurrentPage () {
            this.reload()
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
header {
    min-width: 1320px;
    height: 50px;
    font-size: 14px;
    background: #182131;
    .logo {
        float: left;
        margin-top: 11px;
        margin-left: 25px;
        width: 110px;
    }
    nav {
        float: left;
        margin-left: 120px;
    }
    .nav-item {
        position: relative;
        display: inline-block;
        padding: 0 17px;
        min-width: 90px;
        height: 50px;
        line-height: 50px;
        color: #979BA5;
        text-align: center;
        border-radius: 2px;
        cursor: pointer;
        transition: all .5s linear;
        &:hover {
            color: $whiteDefault;
            .sub-nav {
                display: inline-block;
            }
        }
        &.active {
            color: $whiteDefault;
            background: $blackDefault;
        }
    }
    /*二级导航*/
    .sub-nav {
        display: none;
        position: absolute;
        top: 50px;
        left: 0;
        min-width: 100%;
        background: $whiteDefault;
        border: 1px solid #c4c6cc;
        border-radius: 2px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.16);
        z-index: 1001;
        .sub-nav-item {
            display: block;
            padding: 0 10px;
            height: 35px;
            line-height: 35px;
            color: #63656E;
            white-space: nowrap;
            &.selected {
                color: #313238;
                background: #f0f1f5;
            }
            &:hover {
                color: #313238;
                background: #f0f1f5;
            }
        }
    }
    /*导航右侧区域*/
    .header-right {
        float: right;
        padding-right: 20px;
        .help-doc {
            float: left;
            margin-left: 25px;
            height: 50px;
            font-size: 16px;
            .common-icon-dark-circle-question {
                margin-top: 17px;
                display: inline-block;
                color: #63656e;
                &:hover {
                    color: #616d7d;
                }
            }

        }
        .user-avatar {
            float: left;
            margin-left: 25px;
            height: 50px;
            font-size: 16px;
            color: #63656e;
            .common-icon-dark-circle-avatar {
                display: inline-block;
                margin-top: 17px;
            }
        }
    }
}
</style>
