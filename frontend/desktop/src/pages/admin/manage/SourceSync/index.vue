<template>
    <div class="source-manage">
        <bk-button type="primary" class="sync-btn">{{i18n.sync}}</bk-button>
        <table class="sync-table">
            <thead>
                <tr>
                    <th width="15%" style="padding: 12px 30px;">ID</th>
                    <th width="25%">{{i18n.startTime}}</th>
                    <th width="25%">{{i18n.endTime}}</th>
                    <th width="10%">{{i18n.status}}</th>
                    <th width="10%">{{i18n.triggerType}}</th>
                    <th width="15%">{{i18n.operation}}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="item in list" :key="item.id">
                    <td></td>
                </tr>
                <tr>
                    <td style="padding: 12px 30px;">457</td>
                    <td>2018-10-17 17:35:29 +0800</td>
                    <td>2018-10-17 17:35:29 +0800</td>
                    <td>正在同步</td>
                    <td>手动</td>
                    <td>查看详情</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script>
    export default {
        name: 'SourceManage',
        data () {
            return {
                list: [],
                i18n: {
                    sync: gettext('远程包同步'),
                    startTime: gettext('开始时间'),
                    endTime: gettext('结束时间'),
                    status: gettext('状态'),
                    triggerType: gettext('触发方式'),
                    operation: gettext('操作详情')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-manage {
        padding: 0 60px;
        .sync-btn {
            height: 32px;
            line-height: 32px;
        }
        .sync-table {
            margin-top: 20px;
            width: 100%;
            border: 1px solid #ddE4eb;
            border-collapse: collapse;
            th,
            td {
                padding: 12px;
                font-size: 12px;
                color: #313238;
                border-top: 1px solid #dde4eb;
                text-align: left;
            }
            th {
                font-weight: 500;
                background: #fafbfd;
            }
            td {
                background: #ffffff;
            }
        }
    }
</style>
