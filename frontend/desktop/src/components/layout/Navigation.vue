<template>
    <bk-navigation
        navigation-type="left-right"
        :side-title="platformInfo.name"
        :need-menu="true"
        :class="$route.name === 'taskList' ? 'hide-header-border' : ''"
        :default-open="sideNavOpen"
        @toggle="toggleSideNav">
        <div slot="side-icon" class="logo-area">
            <img :src="platformInfo.appLogo || logo" class="logo" />
        </div>
        <template slot="header">
            <div class="header-title">{{ title }}</div>
            <p v-if="subTitle" class="header-sub-title">
                <i class="bk-icon icon-info-circle"></i>
                {{ subTitle }}
            </p>
            <navigator-head-right></navigator-head-right>
        </template>
        <template slot="menu">
            <bk-navigation-menu
                :key="randomKey"
                :default-active="currentNav"
                :toggle-active="true"
                item-default-icon-color="#949ba5"
                item-child-icon-default-color="#949ba5"
                item-default-color="#96a2b9"
                item-hover-bg-color="#2f3847"
                item-hover-color="#fff"
                item-child-icon-hover-color="#fff"
                item-hover-icon-color="#fff"
                item-active-bg-color="#3a84ff"
                item-active-icon-color="#fff"
                item-active-color="#fff"
                item-child-icon-active-color="#fff"
                sub-menu-open-bg-color="#161c2c">
                <bk-navigation-menu-group
                    v-for="(group, groupIndex) in routerList"
                    :key="groupIndex">
                    <bk-navigation-menu-item
                        v-for="(item, routeIndex) in group"
                        :key="item.id"
                        :has-child="item.children && !!item.children.length"
                        :group="item.group"
                        :icon="item.icon"
                        :disabled="item.disabled"
                        :url="item.url"
                        :id="item.id"
                        :data-test-id="`navigation_list_${item.id}`"
                        @click="onHandleNavClick($event, groupIndex, routeIndex)">
                        <span>{{item.name}}</span>
                        <div slot="child">
                            <bk-navigation-menu-item
                                v-for="(child, childIndex) in item.children"
                                :key="child.id"
                                :id="child.id"
                                :disabled="child.disabled"
                                :icon="child.icon"
                                :default-active="child.active"
                                :data-test-id="`navigation_list_${child.id}`"
                                @click="changeRoute(routerList[groupIndex][routeIndex].children[childIndex])">
                                <span>
                                    {{child.name}}
                                    <span v-if="child.id === 'atomDev'" class="offline-tip">{{ $t('即将下线') }}</span>
                                </span>
                            </bk-navigation-menu-item>
                        </div>
                    </bk-navigation-menu-item>
                </bk-navigation-menu-group>
            </bk-navigation-menu>
        </template>
        <slot name="page-content"></slot>
    </bk-navigation>
</template>
<script>
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { COMMON_ROUTE_LIST, ADMIN_ROUTE_LIST, APPMAKER_ROUTE_LIST } from '@/constants/routes.js'
    import tools from '@/utils/tools.js'
    import NavigatorHeadRight from '@/components/layout/NavigatorHeadRight.vue'
    import bus from '@/utils/bus.js'

    export default {
        inject: ['reload'],
        name: 'Navigation',
        components: {
            NavigatorHeadRight
        },
        data () {
            const sideNavDefault = localStorage.getItem('sideNav')
            const sideNavOpen = sideNavDefault ? sideNavDefault === 'open' : true
            return {
                sideNavOpen,
                title: '',
                currentNav: '',
                logo: require('../../assets/images/logo/logo_icon.svg'),
                randomKey: null
            }
        },
        computed: {
            ...mapState({
                platformInfo: state => state.platformInfo,
                hasAdminPerm: state => state.hasAdminPerm,
                hasStatisticsPerm: state => state.hasStatisticsPerm,
                app_id: state => state.app_id,
                view_mode: state => state.view_mode
            }),
            ...mapState('project', {
                'project_id': state => state.project_id,
                'projectList': state => state.userProjectList
            }),
            commonRouteList () {
                if (!this.project_id && !this.projectList.length) {
                    const commonRouteList = tools.deepClone(COMMON_ROUTE_LIST)
                    return commonRouteList.map(group => {
                        return group.map(item => {
                            if (item.hasProjectId) {
                                item.url = '/guide'
                            }
                            return item
                        })
                    })
                }
                return COMMON_ROUTE_LIST
            },
            routerList () {
                const commonRouteList = this.commonRouteList || COMMON_ROUTE_LIST
                if (this.view_mode === 'appmaker') {
                    return APPMAKER_ROUTE_LIST
                } else if (this.hasAdminPerm) {
                    const adminRouteList = tools.deepClone(ADMIN_ROUTE_LIST)
                    if (!this.hasStatisticsPerm) {
                        // 暂时用写死的方式去掉管理员入口导航的运营数据
                        adminRouteList[0][0].children = adminRouteList[0][0].children.filter(item => item.id !== 'operation')
                    }
                    return commonRouteList.concat(adminRouteList)
                }
                return commonRouteList
            },
            subTitle () {
                if (this.currentNav === 'appMakerList') {
                    return this.$t('流程任务的一种快捷方式，它是基于流程生成并可直接在蓝鲸应用市场&桌面以SaaS方式搜索、添加及打开。这种无需开发、快速生成的类SaaS应用称为“轻应用”。')
                } else if (this.currentNav === 'functionHome') {
                    return this.$t('拥有流程管理权限的人员，通过设置“执行代理人”功能，将流程任务的执行操作交由第三方人员（如：外包、外聘人员），帮助流程管理人员从繁重的执行工作中解放。')
                }
                return ''
            }
        },
        watch: {
            '$route' (val) {
                this.setNavigationTitle(val)
            },
            routerList (val) {
                this.setNavigationTitle(this.$route)
            }
        },
        created () {
            bus.$on('cancelRoute', (val) => {
                const { name } = this.$route
                if (name !== this.currentNav) {
                    this.setNavigationTitle(this.$route)
                    this.randomKey = new Date().getTime()
                }
            })
        },
        methods: {
            ...mapActions('project', [
                'loadUserProjectList'
            ]),
            ...mapMutations('project', [
                'setProjectId'
            ]),
            setNavigationTitle (route) {
                const nav = this.findCurrentNav(route)
                if (nav) {
                    this.title = nav.name
                    this.currentNav = nav.id
                }
            },
            findCurrentNav (route) {
                let nav
                this.routerList.some(group => {
                    return group.some(item => {
                        if (item.id === route.name || (item.subRoutes && item.subRoutes.includes(route.name))) {
                            nav = item
                            return true
                        } else if (item.children) {
                            return item.children.some(childNav => {
                                if (childNav.id === route.name || (childNav.subRoutes && childNav.subRoutes.includes(route.name))) {
                                    nav = childNav
                                    return true
                                }
                            })
                        }
                    })
                })
                return nav
            },
            changeRoute (nav) {
                const route = {
                    path: nav.url
                }
                if (nav.hasProjectId) {
                    route.path = `${nav.url}${this.project_id}/`
                }
                if (this.$route.name === nav.id) {
                    this.$router.push(route)
                    this.$nextTick(() => {
                        this.reload()
                    })
                } else {
                    this.$router.push(route)
                }
                this.title = nav.name
            },
            async onHandleNavClick (id, groupIndex, routeIndex) {
                if (this.view_mode === 'appmaker') { // 轻应用跳转特殊处理
                    const { template_id } = this.$route.query
                    if (id === 'appmakerTaskCreate') {
                        this.$router.push({
                            name: 'appmakerTaskCreate',
                            params: {
                                app_id: this.app_id,
                                project_id: this.project_id,
                                step: 'selectnode'
                            },
                            query: { template_id }
                        })
                    } else {
                        this.$router.push({
                            name: 'appmakerTaskHome',
                            params: {
                                app_id: this.app_id,
                                project_id: this.project_id
                            },
                            query: { template_id }
                        })
                    }
                } else {
                    const routeInfo = this.routerList[groupIndex][routeIndex]
                    // 如果没有项目列表，切换路由时则去拉取用户项目列表
                    if (!this.projectList.length && (routeInfo.hasProjectId || routeInfo.id === 'home')) {
                        await this.loadUserProjectList({
                            params: { is_disable: false }
                        })
                        if (this.projectList.length && !this.project_id) {
                            const projectId = this.projectList[0].id
                            this.setProjectId(projectId)
                        }
                    }
                    // 项目列表和默认项目id记录后再进下路由跳转
                    this.$nextTick(() => {
                        this.changeRoute(this.routerList[groupIndex][routeIndex])
                    })
                }
            },
            // onHandleSubNavClick (groupIndex, routeIndex, childIndex) {
            //     if (this.$route.name === route.routerName) {
            //         if (tools.isDataEqual(this.$route.query, config.query)) {
            //             return this.reload()
            //         } else {
            //             this.$router.push(config)
            //             this.$nextTick(() => {
            //                 this.reload()
            //             })
            //             return
            //         }
            //     }
            //     this.changeRoute(this.routerList[groupIndex][routeIndex].children[childIndex])
            // },
            toggleSideNav (val) {
                localStorage.setItem('sideNav', val ? 'open' : 'close')
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';

    .header-title {
        flex-shrink: 0;
        font-size: 16px;
        color: #313238;
    }
    .header-sub-title {
        flex: 1;
        display: flex;
        align-items: center;
        font-size: 12px;
        line-height: 20px;
        margin: 0 15px;
        color: #63656e;
        word-break: break-all;
        text-overflow: ellipsis;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        overflow: hidden;
        .icon-info-circle {
            margin-right: 9px;
        }
    }

    .bk-navigation {
        &.hide-header-border {
            /deep/ .container-header {
                border-color: transparent;
                box-shadow: 0;
            }
        }
        /deep/ {
            .bk-navigation-wrapper {
                min-width: 1366px;
                .navigation-container {
                    max-width: unset !important;
                    .container-content {
                        padding: 0;
                        @include scrollbar;
                    }
                }
                .navigation-nav {
                    z-index: 111;
                    .nav-slider {
                        background-color: #182132 !important;
                    }
                    .nav-slider-list {
                        padding-top: 0;
                    }
                }
                .container-header {
                    justify-content: space-between;
                }
            }
            .bk-navigation-menu-group,
            .bk-navigation-menu-group .group-name-wrap {
                display: flex;
                align-items: center;
                color: #66748f;
                width: 100%;
            }
            .bk-navigation-menu-group {
                border-top: 1px solid rgba(255,255,255,0.06);
            }
            .navigation-sbmenu .navigation-menu-item:hover,
            .navigation-sbmenu-title:hover {
                background: #2f3847 !important;
                .navigation-sbmenu-title-icon,
                .navigation-sbmenu-title-content {
                    color: #fff !important;
                }
            }
            .navigation-menu-item-default-icon {
                height: 4px;
                width: 4px;
            }
        }
        .offline-tip {
            display: inline-block;
            line-height: 22px;
            font-size: 12px;
            transform: scale(.8);
            color: #ff9c01;
            padding: 0 4px;
            border: 1px solid #ffb848;
            border-radius: 2px;
        }
    }
</style>
