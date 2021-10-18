<template>
    <bk-navigation
        navigation-type="left-right"
        :side-title="$t('标准运维')"
        :need-menu="true"
        :default-open="sideNavOpen"
        @toggle="toggleSideNav">
        <div slot="side-icon" class="logo-area">
            <img :src="logo" class="logo" />
        </div>
        <template slot="header">
            <div class="header-title">{{ title }}</div>
            <navigator-head-right></navigator-head-right>
        </template>
        <template slot="menu">
            <bk-navigation-menu :default-active="currentNav" :toggle-active="true">
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
                                @click="changeRoute(routerList[groupIndex][routeIndex].children[childIndex])">
                                <span>{{child.name}}</span>
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
    import { mapState } from 'vuex'
    import { COMMON_ROUTE_LIST, ADMIN_ROUTE_LIST, APPMAKER_ROUTE_LIST } from '@/constants/routes.js'
    import tools from '@/utils/tools.js'
    import NavigatorHeadRight from '@/components/layout/NavigatorHeadRight.vue'

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
                logo: require('../../assets/images/logo/logo_icon.svg')
            }
        },
        computed: {
            ...mapState({
                hasAdminPerm: state => state.hasAdminPerm,
                hasStatisticsPerm: state => state.hasStatisticsPerm,
                app_id: state => state.app_id,
                view_mode: state => state.view_mode
            }),
            ...mapState('project', {
                'project_id': state => state.project_id
            }),
            routerList () {
                if (this.view_mode === 'appmaker') {
                    return APPMAKER_ROUTE_LIST
                } else if (this.hasAdminPerm) {
                    const adminRouteList = tools.deepClone(ADMIN_ROUTE_LIST)
                    if (!this.hasStatisticsPerm) {
                        // 暂时用写死的方式去掉管理员入口导航的运营数据
                        adminRouteList[0][0].children = adminRouteList[0][0].children.filter(item => item.id !== 'operation')
                    }
                    return COMMON_ROUTE_LIST.concat(adminRouteList)
                }
                return COMMON_ROUTE_LIST
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
        methods: {
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
            },
            onHandleNavClick (id, groupIndex, routeIndex) {
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
                    this.changeRoute(this.routerList[groupIndex][routeIndex])
                }
                this.$emit('navChangeRoute')
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
        font-size: 16px;
        color: #313238;
    }

    .bk-navigation >>> {
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
    }
</style>
