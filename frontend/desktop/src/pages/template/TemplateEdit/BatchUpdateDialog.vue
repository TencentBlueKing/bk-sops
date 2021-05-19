<template>
    <bk-dialog
        class="batch-update-dialog"
        v-model="isShow"
        :close-icon="false"
        :fullscreen="true">
        <div slot="header" class="header-wrapper">
            <h4>批量更新子流程</h4>
            <div class="legend-area">
                <span class="legend-item delete">删除</span>
                <span class="legend-item add">新增</span>
            </div>
            <i class="bk-dialog-close bk-icon icon-close"></i>
        </div>
    </bk-dialog>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'BatchUpdateDialog',
        props: {
            show: {
                type: Boolean,
                default: false
            },
            list: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                isShow: this.show,
                subflowFormsLoading: false,
                oldForms: [],
                newForms: []
            }
        },
        watch: {
            show (val) {
                this.isShow = val
                this.loadSubflowForms()
            }
        },
        methods: {
            ...mapActions('template', [
                'getBatchForms'
            ]),
            async loadSubflowForms () {
                try {
                    this.subflowFormsLoading = true
                    const oldVersionTpls = []
                    const newVersionTpls = []
                    this.list.forEach(item => {
                        oldVersionTpls.push({
                            id: item.template_id,
                            version: item.version
                        })
                        newVersionTpls.push({
                            id: item.template_id
                        })
                    })
                    Promise.all([this.getBatchForms(oldVersionTpls), this.getBatchForms(newVersionTpls)]).then(res => {
                        this.oldForms = res[0].data
                        this.newForms = res[1].data
                    })
                } catch (e) {
                    console.error(e)
                } finally {
                    this.subflowFormsLoading = false
                }
            },
            onConfirm () {
                this.$emit('batchUpdate')
            },
            onCancel () {
                this.$emit('show:update', false)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .header-wrapper {
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 80px 0 26px;
        height: 54px;
        line-height: 1;
        border-bottom: 1px solid #dcdee5;
        & > h4 {
            margin: 0;
            font-weight: normal;
            font-size: 14px;
            color: #313238;
        }
        .legend-item {
            position: relative;
            display: inline-block;
            margin-left: 18px;
            padding-left: 20px;
            font-size: 14px;
            color: #63656e;
            line-height: 1;
            &:before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 3px;
            }
            &.delete:before {
                border: 1px solid rgba(251,133,121,0.16);
                background: #ffeeed;
            }
            &.add:before {
                border: 1px solid rgba(76,164,90,0.22);
                background: #e5ffe9;
            }
        }
        .bk-dialog-close {
            position: absolute;
            right: 20px;
            top: 16px;
            width: 26px;
            height: 26px;
            line-height: 26px;
            text-align: center;
            border-radius: 50%;
            font-size: 24px;
            font-weight: bold;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                background-color: #f0f1f5;
            }
        }
    }
</style>
<style lang="scss">
    .batch-update-dialog {
        .bk-dialog-tool {
            display: none;
        }
        .bk-dialog-header {
            padding: 0;
        }
    }
</style>
