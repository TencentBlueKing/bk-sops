<template>
    <div class="source-manage">
        <div class="operate-area">
            <bk-button type="primary">{{i18n.create}}</bk-button>
            <bk-button type="primary">{{i18n.edit}}</bk-button>
        </div>
        <div class="empty-data">
            <p>{{i18n.noData}}<router-link to="/admin/source_manange/package/">{{i18n.create}}</router-link>{{i18n.sourceManage}}</p>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'SourceSync',
        data () {
            return {
                i18n: {
                    create: gettext('新建'),
                    edit: gettext('编辑'),
                    noData: gettext('暂无数据，'),
                    sourceManage: gettext('包源管理')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-manage {
        height: calc(100% - 80px);
    }
    .operate-area {
        .bk-button {
            height: 32px;
            line-height: 32px;
        }
    }
    .empty-data {
        display: flex;
        justify-content: center;
        align-items: center;
        height: calc(100% - 32px);
        font-size: 14px;
        color: #c4c6cc;
        a {
            color: #3a84ff;
        }
    }
</style>
