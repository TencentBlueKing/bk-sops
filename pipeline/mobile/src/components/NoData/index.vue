<template>
    <van-cell title="" :value="i18n.noData" />
</template>

<script>
    export default {
        name: 'NoData',
        data () {
            return {
                i18n: {
                    noData: window.gettext('暂无数据')
                }
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
