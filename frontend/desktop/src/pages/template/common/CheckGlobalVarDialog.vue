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
    import tools from '@/utils/tools.js'
    import { mapState, mapMutations } from 'vuex'
    export default {
        name: 'CheckGlobalVarDialog',
        data () {
            return {
                isVarKeysDialogShow: false,
                illegalKeys: [] // 不合规的变量key值
            }
        },
        computed: {
            ...mapState({
                'constants': state => state.template.constants
            })
        },
        methods: {
            ...mapMutations('template/', [
                'setConstants'
            ]),
            checkGlobalVar () {
                const variableKeys = Object.keys(this.constants)
                const illegalKeys = []
                variableKeys.forEach(key => {
                    if (/(^\${(_env_|_system\.))|(^(_env_|_system\.))/.test(key)) {
                        illegalKeys.push(key)
                    }
                })
                if (illegalKeys.length) {
                    this.illegalKeys = illegalKeys
                    this.isVarKeysDialogShow = true
                    return true
                }
                return false
            },
            handleDialogConfirm () {
                const constants = tools.deepClone(this.constants)
                this.illegalKeys.forEach(key => {
                    this.$delete(constants, key)
                })
                this.setConstants(constants)
                this.isVarKeysDialogShow = false
                this.$parent.saveTemplate()
            },
            handleDialogCancel () {
                this.illegalKeys = []
                this.isVarKeysDialogShow = false
            }
        }
    }
</script>

<style>

</style>
