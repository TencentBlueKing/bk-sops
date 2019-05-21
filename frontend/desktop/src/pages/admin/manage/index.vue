<template>
    <div class="page-manage">
        <navi-header :routers="routers" :title="i18n.title"></navi-header>
        <router-view></router-view>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import NaviHeader from '../components/NaviHeader.vue'

    const ROUTERS = [
        {
            text: gettext('包源管理'),
            name: 'sourceManage',
            path: '/admin/manage/source_manage/'
        },
        {
            text: gettext('包源同步'),
            name: 'sourceSync',
            path: '/admin/manage/source_sync/'
        }
    ]

    export default {
        name: 'Manage',
        components: {
            NaviHeader
        },
        data () {
            return {
                routers: ROUTERS,
                i18n: {
                    title: gettext('管理后台')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .page-manage {
        padding: 0 60px;
        min-width: 1320px;
        height: calc(100% - 50px);
        background: #f4f7fa;
    }
</style>
