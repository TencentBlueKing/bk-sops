<template>
    <bk-dialog
        :value="isVarKeysDialogShow"
        theme="primary"
        width="500"
        :mask-close="false"
        @cancel="handleDialogCancel">
        <p>{{ $t('自定义变量中存在系统变量/项目变量的key，需要清除后才能保存，是否一键清除？(可通过【模版数据-constants】进行确认)') }}</p>
        <p class="mt10">{{ $t('问题变量有：') + illegalKeys.join(',') }}</p>
        <template slot="footer">
            <bk-button theme="primary" @click="handleDialogConfirm">{{ $t('清除') }}</bk-button>
            <bk-button @click="handleDialogCancel">{{ $t('取消') }}</bk-button>
        </template>
    </bk-dialog>
</template>

<script>
    import varDirtyData from '@/mixins/varDirtyData.js'
    export default {
        name: 'CheckGlobalVarDialog',
        mixins: [varDirtyData],
        data () {
            return {
                isVarKeysDialogShow: false
            }
        },
        methods: {
            handleDialogConfirm () {
                this.clearVarDirtyData()
                this.isVarKeysDialogShow = false
                this.$parent.saveTemplate()
            },
            handleDialogCancel () {
                this.isVarKeysDialogShow = false
            }
        }
    }
</script>
