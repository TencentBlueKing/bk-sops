<template>
    <div class="notify-type-wrapper">
        <bk-form
            ref="notifyConfigForm"
            class="notify-form-area"
            :model="formData"
            :label-width="labelWidth"
            :rules="rules">
            <bk-form-item property="notifyType" :label="notifyTypeLabel" data-test-id="notifyTypeConfig_form_notifyType">
                <bk-table
                    class="notify-type-table"
                    :style="{ width: tableWidth ? `${tableWidth}px` : '100%' }"
                    :data="formData.notifyType"
                    v-bkloading="{ isLoading: notifyTypeLoading, opacity: 1, zIndex: 100 }">
                    <bk-table-column
                        v-for="(col, index) in allNotifyTypeList"
                        :key="index"
                        :render-header="getNotifyTypeHeader">
                        <template slot-scope="props">
                            <bk-switcher
                                v-if="col.type"
                                size="small"
                                theme="primary"
                                :disabled="isViewMode"
                                :value="props.row.includes(col.type)"
                                @change="onSelectNotifyType(props.$index, col.type, $event)">
                            </bk-switcher>
                            <span v-else>{{ props.$index === 0 ? $t('成功') : $t('失败') }}</span>
                        </template>
                        <div class="empty-data" slot="empty">
                            <NoData></NoData>
                        </div>
                    </bk-table-column></bk-table>
            </bk-form-item>
            <bk-form-item property="notifyGroup" :label="notifyGroupLabel" data-test-id="notifyTypeConfig_form_notifyGroup">
                <bk-checkbox-group
                    class="bk-checkbox-group"
                    :value="formData.receiverGroup"
                    v-bkloading="{ isLoading: notifyGroupLoading, opacity: 1, zIndex: 100 }"
                    @change="onReceiverGroup">
                    <bk-checkbox
                        v-for="item in notifyGroup"
                        :key="item.id"
                        :disabled="isViewMode"
                        :value="item.id">
                        {{item.name}}
                    </bk-checkbox>
                </bk-checkbox-group>
            </bk-form-item>
        </bk-form>
    </div>
</template>

<script>
    import { mapState, mapActions, mapMutations } from 'vuex'
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        components: {
            NoData
        },
        props: {
            notifyTypeLabel: {
                type: String,
                default: i18n.t('通知方式')
            },
            notifyGroupLabel: {
                type: String,
                default: i18n.t('通知分组')
            },
            notifyType: {
                type: Array,
                default: () => [[]]
            },
            notifyTypeList: {
                type: Array,
                default: () => []
            },
            receiverGroup: {
                type: Array,
                default: () => []
            },
            tableWidth: {
                type: Number,
                default: 0
            },
            labelWidth: {
                type: Number,
                default: 100
            },
            rules: {
                type: Object,
                default: () => ({})
            },
            common: [String, Number],
            isViewMode: {
                type: Boolean,
                default: false
            },
            project_id: [String, Number]
        },
        data () {
            return {
                formData: {
                    notifyType: [[]],
                    receiverGroup: []
                },
                notifyTypeLoading: false,
                allNotifyTypeList: [],
                notifyGroupLoading: false,
                projectNotifyGroup: []
            }
        },
        computed: {
            ...mapState({
                'projectBaseInfo': state => state.template.projectBaseInfo
            }),
            notifyGroup () {
                let list = []
                if (this.projectBaseInfo.notify_group) {
                    const defaultList = list.concat(this.projectBaseInfo.notify_group.map(item => {
                        return {
                            id: item.value,
                            name: item.text
                        }
                    }))
                    list = defaultList.concat(this.projectNotifyGroup)
                }
                return list
            }
        },
        watch: {
            notifyType: {
                handler (val) {
                    this.formData.notifyType = tools.deepClone(val)
                },
                immediate: true
            },
            receiverGroup: {
                handler (val) {
                    this.formData.receiverGroup = tools.deepClone(val)
                },
                immediate: true
            }
        },
        created () {
            this.getNotifyTypeList()
            if (!this.common) {
                this.getProjectNotifyGroup()
            }
        },
        methods: {
            ...mapActions([
                'getNotifyTypes',
                'getNotifyGroup'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapMutations('template/', [
                'setProjectBaseInfo'
            ]),
            async getNotifyTypeList () {
                try {
                    this.notifyTypeLoading = true
                    const res = await this.getNotifyTypes()
                    this.allNotifyTypeList = [].concat(this.notifyTypeList, res.data)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.notifyTypeLoading = false
                }
            },
            getNotifyTypeHeader (h, data) {
                const col = this.allNotifyTypeList[data.$index]
                if (col.type) {
                    return h('div', { 'class': 'notify-table-heder' }, [
                        h('img', { 'class': 'notify-icon', attrs: { src: `data:image/png;base64,${col.icon}` } }, []),
                        h('p', {
                            class: 'label-text',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [
                            col.label
                        ])
                    ])
                } else {
                    return h('p', {
                        class: 'label-text',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [
                        col.text
                    ])
                }
            },
            onSelectNotifyType (row, type, val) {
                const data = this.formData.notifyType[row]
                if (val) {
                    data.push(type)
                } else {
                    const index = data.findIndex(item => item === type)
                    if (index > -1) {
                        data.splice(index, 1)
                    }
                }
                this.$emit('change', this.formData)
            },
            onReceiverGroup (val) {
                this.formData.receiverGroup = val
                this.$emit('change', this.formData)
            },
            async getProjectNotifyGroup () {
                try {
                    this.notifyGroupLoading = true
                    if (!this.projectBaseInfo.notify_group) {
                        const resp = await this.loadProjectBaseInfo()
                        this.setProjectBaseInfo(resp.data)
                    }
                    const res = await this.getNotifyGroup({ project_id: this.project_id })
                    this.projectNotifyGroup = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.notifyGroupLoading = false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import "@/scss/config.scss";
    .notify-type {
        width: 100%;
    }
    .bk-form-checkbox {
        margin-right: 20px;
        margin-top: 6px;
        min-width: 96px;
        /deep/ .bk-checkbox-text {
            color: $greyDefault;
            font-size: 12px;
        }
        &.is-disabled /deep/.bk-checkbox-text {
            color: #c4c6cc;
        }
        &.is-checked /deep/.bk-checkbox-text  {
            color: #606266;
        }
    }
    /deep/ .bk-checkbox-text {
        display: inline-flex;
        align-items: center;
        width: 100px;
    }
    .notify-type-table {
        min-height: 86px;
        /deep/ .notify-table-heder {
            display: flex;
            align-items: center;
            .notify-icon {
                margin-right: 4px;
                width: 18px;
            }
        }
    }
</style>
