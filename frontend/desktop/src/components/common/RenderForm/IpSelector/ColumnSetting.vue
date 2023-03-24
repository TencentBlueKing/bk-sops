<template>
    <div class="column-setting">
        <div
            class="host-table-column-setting">
            <div class="setting-header">
                表格设置
            </div>
            <bk-checkbox-group v-model="selectedList" class="column-list">
                <div
                    v-for="item in columnList"
                    :key="item.name"
                    class="column-item">
                    <span
                        v-if="item.id === 'bk_host_innerip'"
                        v-bk-tooltips="{
                            content: 'IP 与 IPv6 至少需保留一个',
                            disabled: selectedList.includes('bk_host_innerip_v6'),
                            zIndex: 2223
                        }">
                        <bk-checkbox
                            :disabled="!selectedList.includes('bk_host_innerip_v6')"
                            :value="item.id">
                            {{ item.name }}
                        </bk-checkbox>
                    </span>
                    <span
                        v-else-if="item.id === 'bk_host_innerip_v6'"
                        v-bk-tooltips="{
                            content: 'IP 与 IPv6 至少需保留一个',
                            disabled: selectedList.includes('bk_host_innerip'),
                            zIndex: 2223
                        }">
                        <bk-checkbox
                            :disabled="!selectedList.includes('bk_host_innerip')"
                            :value="item.id">
                            {{ item.name }}
                        </bk-checkbox>
                    </span>
                    <template v-else>
                        <bk-checkbox :value="item.id">
                            {{ item.name }}
                        </bk-checkbox>
                    </template>
                </div>
            </bk-checkbox-group>
            <div class="setting-footer">
                <bk-button
                    style="margin-right: 8px;"
                    theme="primary"
                    :disabled="!editable"
                    @click="handleSubmitSetting">
                    确定
                </bk-button>
                <bk-button @click="handleHideSetting">
                    取消
                </bk-button>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            columnList: {
                type: Array,
                default: () => ([])
            },
            editable: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                selectedList: []
            }
        },
        computed: {
            popoverInstance () {
                return this.$parent.instance
            }
        },
        watch: {
            columnList: {
                handler (val) {
                    if (val.length) {
                        this.selectedList = val.filter(item => item.checked).map(item => item.id)
                    }
                },
                immediate: true
            },
            popoverInstance () {
                this.initCallback()
            }
        },
        methods: {
            initCallback () {
                this.popoverInstance.set({
                    onHidden: () => {
                        if (this.isConfirm) {
                            this.$emit('change', this.selectedList)
                        } else {
                            this.$emit('cancel')
                        }
                        this.isConfirm = false
                    }
                })
            },
            handleSubmitSetting () {
                this.isConfirm = true
                this.popoverInstance.hide()
            },
            handleHideSetting () {
                this.isConfirm = false
                this.popoverInstance.hide()
            }
        }
    }
</script>

<style lang="scss">
    .bk-table-setting-popover-content-theme {
        padding-top: 4px !important;
    }
</style>
<style lang="scss" scoped>
.common-icon-bkflow-setting {
    height: 100%;
    width: 100%;
    line-height: 39px;
}
.host-table-column-setting {
    width: 545px;
    padding-top: 10px;
    margin: -5px -9px;
    background: #fff;
    border-radius: 2px;
    color: #63656e;
    border: 1px solid #dcdee5;
    box-shadow: 0 0 5px 0 rgba(0,0,0,0.09);
    .setting-header {
        padding: 0 24px;
        font-size: 20px;
        line-height: 20px;
        color: #313238;
    }

    .column-list {
        display: flex;
        flex-wrap: wrap;
        padding: 0 24px 36px;
    }

    .column-item {
        display: flex;
        align-items: center;
        width: 165px;
        height: 32px;
        padding: 0 8px;
        margin-top: 16px;
        border-radius: 2px;

        &:hover {
            background: #f5f7fa;

            .column-item-drag {
                display: flex;
            }
        }

        .bk-checkbox-text {
            font-size: 12px;
        }
    }

    .setting-footer {
        display: flex;
        height: 50px;
        padding-right: 24px;
        background: #fafbfd;
        border-top: 1px solid #dcdee5;
        justify-content: flex-end;
        align-items: center;
    }

    .ghost {
        background: #c8ebfb;
        opacity: 50%;
    }
}
</style>
