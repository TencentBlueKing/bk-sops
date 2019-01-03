/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <header>
        <img :src="logo" class="logo"/>
        <nav>
            <div class="navigator" v-if="!appmakerDataLoading">
                <router-link
                    v-for="route in route_list"
                    :key="route.key"
                    :to="getGotoPath(route)"
                    :class="{
                        'nav-item': true,
                        'active-module': getPathActivedState(route.key)
                    }"
                    tag="a">{{route.name}}</router-link>
                <a target="_blank" href="http://docs.bk.tencent.com/product_white_paper/gcloud/" class="nav-item" v-if="view_mode !== 'analysis'">{{ i18n.help }}</a>
            </div>
        </nav>
        <div class="header-right">
            <div class="biz-list" v-if="showHeaderRight && view_mode !== 'analysis'">
                <bk-selector
                    :list="businessList"
                    :selected.sync="currentCcId"
                    @item-selected="onSelectBiz">
                </bk-selector>
            </div>
            <a
                :href="`${site_url}`"
                target="_self"
                v-if="view_mode === 'analysis' && isSuperUser"
                class="nav-item">
                {{i18n.back}}
            </a>
            <div v-if="username" class="user-name">{{username}}</div>
        </div>
    </header>
</template>
<script>
import '@/utils/i18n.js'
import { mapState, mapMutations, mapActions } from 'vuex'
import { errorHandler } from '@/utils/errorHandler.js'
import { setAtomConfigApiUrls } from '@/config/setting.js'
const ROUTE_LIST = {
    functor_router_list: [
        {
            key: 'function',
            path: '/function/home/',
            name: gettext('职能化中心')
        }
    ],
    auditor_router_list: [
        {
            key: 'audit',
            path: '/audit/home/',
            name: gettext('审计中心')
        }
    ],
    maintainer_router_list: [
        {
            key: 'business',
            path: '/business/home/',
            name: gettext('业务首页')
        },
        {
            key: 'template',
            path: '/template/home/',
            name: gettext('流程模板')
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
        }
    ]
}

export default {
    name: 'Navigator',
    props: ['appmakerDataLoading'],
    data () {
        return {
            i18n: {
                help: gettext("帮助文档"),
                analysisName: gettext("运营数据"),
                back: gettext('返回首页')
            },
            logo: require('../../assets/images/logo/' + gettext('logo-zh') + '.svg'),
            analysisLogo: require('../../assets/images/analysis.png')
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
            run_ver: state => state.run_ver,
            bizList: state => state.bizList,
            templateId: state => state.templateId,
            notFoundPage: state => state.notFoundPage,
            isSuperUser: state => state.isSuperUser
        }),
        businessList () {
            return this.bizList.map(item => {
                return {
                    id: item.cc_id,
                    name: item.cc_name
                }
            })
        },
        currentCcId: {
            get () {
                return this.cc_id
            },
            set (id) {
                this.setBizId(id)
            }
        },
        showHeaderRight () {
            if (
                this.userType === 'maintainer' &&
                this.view_mode !== 'appmaker' &&
                this.bizList.length
            ) {
                return true
            }
            return false
        },
        route_list () {
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
            }  else if (this.view_mode === 'analysis') {
                return [
                    {
                        key: 'analysisTemplate',
                        path: '/analysis/template/',
                        name: gettext('流程统计')
                    },
                    {
                        key: 'analysisInstance',
                        path: '/analysis/instance/',
                        name: gettext('任务统计')
                    },
                    {
                        key: 'analysisAtom',
                        path: '/analysis/atom/',
                        name: gettext('原子统计')
                    },
                    {
                        key: 'analysisAppmaker',
                        path: '/analysis/appmaker/',
                        name: gettext('轻应用统计')
                    }
                ]
            }
            else {
                let routes = ROUTE_LIST[`${this.userType}_router_list`]
                if (this.run_ver === 'community') {
                    routes = routes.filter(item => item.key !== 'appmaker')
                }
                return routes
            }
        }
    },
    mounted () {
        if (this.userType === 'maintainer' && this.view_mode !== 'appmaker') {
            this.getBizList()
        }
    },
    methods: {
        ...mapActions([
            'getBizList',
            'changeDefaultBiz'
        ]),
        ...mapMutations([
            'setBizId'
        ]),
        getPathActivedState (key) {
            if (this.view_mode === 'appmaker') {
                if (this.$route.name === 'appmakerTaskExecute' || this.$route.name === 'appmakerTaskHome') {
                    return key === 'appmakerTaskList'
                }
                else {
                    return key === 'appmakerTaskCreate'
                }
            }
            else if (this.view_mode === 'analysis') {
                if (this.$route.name === 'analysisTemplate') {
                    return key === 'analysisTemplate'
                } else if (this.$route.name === 'analysisInstance') {
                    return key === 'analysisInstance'
                } else if (this.$route.name === 'analysisAppmaker') {
                    return key === 'analysisAppmaker'
                } else if (this.$route.name === 'analysisAtom') {
                    return key === 'analysisAtom'
                }
            }
            if (this.userType === 'functor') {
                return key === 'function'
            } else if (this.userType === 'auditor') {
                return key === 'audit'
            }
            const regx = new RegExp('^\/' + key)
            return regx.test(this.$route.path)
        },
        getGotoPath (route) {
            if (this.notFoundPage) {
                return '/'
            }
            if (route.key === 'appmakerTaskCreate') {
                return `${route.path}?template_id=${this.templateId}`
            } else if (this.userType !== 'maintainer' || this.view_mode === 'analysis') {
                return `${route.path}`
            } else {
                return `${route.path}${this.cc_id}/`
            }
        },
        async onSelectBiz (id) {
            try {
                const res = await this.changeDefaultBiz()
                if (res.result) {
                    setAtomConfigApiUrls(this.site_url, this.cc_id)
                    this.$router.push({path: `/business/home/${id}/`})
                } else {
                    errorHandler(res, this)
                }
            } catch (e) {
                errorHandler(e, this)
            }
        }
    }
}
</script>
<style lang="scss">
    @import '@/scss/config.scss';
    header {
        min-width: $minWidth;
        height: 60px;
        font-size: 14px;
        background: $blackBack;
        .logo {
            float: left;
            margin-top: 14px;
            margin-left: 20px;
            width: 120px;
        }
        .analysisLogo {
            float: left;
            margin-top: 17px;
            margin-left: 20px;
        }
        nav {
            float: left;
            margin-top: 12px;
            margin-left: 100px;
        }
        .nav-item {
            display: inline-block;
            width: 90px;
            height: 36px;
            line-height: 36px;
            color: $greyDark;
            text-align: center;
            border-radius: 2px;
            cursor: pointer;
            transition: all .5s linear;
            &:hover {
                color: $whiteDefault;
                background-color: $blackBack;
            }
            &.active-module {
                color: $whiteDefault;
                background: $blueDefault;
            }
        }
        .header-right {
            float: right;
            padding-right: 20px;
            .biz-list {
                display: inline-block;
                vertical-align: top;
                .bk-selector-input {
                    height: 60px;
                    line-height: 60px;
                    border: none;
                    background: #333;
                    color: #fff;
                }
                .bk-selector-icon {
                    top: 23px;
                }
            }
            .user-name {
                display: inline-block;
                margin-left: 20px;
                height: 60px;
                line-height: 60px;
                font-size: 14px;
                color: #666;
            }
        }
    }
</style>
