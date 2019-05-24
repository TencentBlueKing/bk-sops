<template>
    <div class="source-manage">
        <div class="operate-area">
            <router-link
                to="/admin/manage/source_edit/package_edit/"
                class="operate-btn bk-button bk-primary">
                {{ false ? i18n.create : i18n.edit }}
            </router-link>
        </div>
        <div class="section-title">
            <div class="title-wrapper">
                <h4>{{i18n.mainSource}}</h4>
                <i
                    class="title-tooltip bk-icon icon-info-circle"
                    v-bktooltips.right="i18n.sourceTip">
                </i>
            </div>
        </div>
        <template>
            <package-table></package-table>
            <package-table></package-table>
        </template>
        <NoData v-if="false"></NoData>
        <div class="section-title">
            <div class="title-wrapper">
                <h4>{{i18n.localCache}}</h4>
                <i
                    class="title-tooltip bk-icon icon-info-circle"
                    v-bktooltips.right="i18n.cacheTip">
                </i>
            </div>
        </div>
        <local-cache v-if="true"></local-cache>
        <NoData v-else></NoData>
        <div class="empty-data" v-if="false">
            <p>{{i18n.noData}}<router-link to="/admin/manage/source_edit/package_edit/">{{i18n.create}}</router-link>{{i18n.sourceManage}}</p>
        </div>
    </div>
</template>
<script>
    import PackageTable from './PackageTable.vue'
    import LocalCache from './LocalCache.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'SourceSync',
        components: {
            PackageTable,
            LocalCache,
            NoData
        },
        data () {
            return {
                i18n: {
                    create: gettext('新建'),
                    edit: gettext('编辑'),
                    noData: gettext('暂无数据，'),
                    sourceManage: gettext('包源管理'),
                    mainSource: gettext('主包源'),
                    localCache: gettext('本地缓存'),
                    sourceTip: gettext('Xxxxxxxx'),
                    cacheTip: gettext('Yyyyyyyyy')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-manage {
        height: calc(100% - 80px);
        padding-bottom: 60px;
    }
    .operate-area {
        .operate-btn {
            height: 32px;
            line-height: 32px;
        }
    }
    .section-title {
        margin: 20px 0;
        font-size: 14px;
        .title-wrapper {
            display: flex;
            align-items: center;
        }
        h4 {
            display: inline-block;
            margin: 0;
            color: #313238;
            line-height: 1;
        }
        .title-tooltip {
            display: inline-block;
            margin-left: 10px;
            color: #c4c6cc;
            font-size: 16px;
            &:hover {
                color: #f4aa1a;
            }
        }
    }
    .empty-data {
        display: flex;
        justify-content: center;
        align-items: center;
        height: calc(100% - 130px);
        font-size: 14px;
        color: #c4c6cc;
        a {
            color: #3a84ff;
        }
    }
    .no-data-wrapper {
        margin-top: 30px;
        background: transparent;
        color: #c4c6cc;
    }
</style>
