<template>
    <div class="notify-type-wrapper">
        <div
            v-if="isNotifyType"
            :style="{ 'width': `${defaultWidth}px` }"
            v-bkloading="{ isLoading: notifyTypeLoading, opacity: 1, zIndex: 100 }">
            <bk-table class="notify-type-table" :data="selectNotifyType">
                <bk-table-column v-for="(col, index) in AllNotifyTypeList" :key="index" :render-header="getNotifyTypeHeader">
                    <template slot-scope="props">
                        <bk-switcher
                            size="small"
                            theme="primary"
                            :value="props.row.includes(col.type)"
                            @change="onSelectNotifyType(props.$index, col.type, $event)">
                        </bk-switcher>
                    </template>
                </bk-table-column>
            </bk-table>
        </div>
        <bk-checkbox-group
            v-if="isNotifyGroup"
            :value="selectReceiverGroup"
            v-bkloading="{ isLoading: notifyGroupLoading, opacity: 1, zIndex: 100 }"
            @change="onReceiverGroup">
            <bk-checkbox
                v-for="item in notifyGroup"
                :key="item.id"
                :value="item.id">
                {{item.name}}
            </bk-checkbox>
        </bk-checkbox-group>
    </div>
</template>

<script>
    import { mapState, mapActions, mapMutations } from 'vuex'
    import tools from '@/utils/tools.js'
    export default {
        props: {
            isNotifyType: {
                type: Boolean,
                default: true
            },
            isNotifyGroup: {
                type: Boolean,
                default: true
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
            defaultWidth: {
                type: Number,
                default: 500
            }
        },
        data () {
            return {
                notifyTypeLoading: true,
                AllNotifyTypeList: [],
                selectNotifyType: [],
                notifyGroupLoading: true,
                projectNotifyGroup: [],
                selectReceiverGroup: []
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
                    this.selectNotifyType = tools.deepClone(val)
                },
                immediate: true
            },
            receiverGroup: {
                handler (val) {
                    this.selectReceiverGroup = tools.deepClone(val)
                },
                immediate: true
            }
        },
        created () {
            this.getNotifyTypeList()
            this.getProjectNotifyGroup()
        },
        methods: {
            ...mapActions([
                'queryUserPermission',
                'getNotifyTypes',
                'getNotifyGroup'
            ]),
            ...mapActions('template/', [
                'loadProjectBaseInfo'
            ]),
            ...mapMutations('template/', [
                'setTemplateData',
                'setProjectBaseInfo'
            ]),
            async getNotifyTypeList () {
                try {
                    this.notifyTypeLoading = true
                    const res = await this.getNotifyTypes()
                    this.AllNotifyTypeList = [].concat(this.notifyTypeList, res.data)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.notifyTypeLoading = false
                }
            },
            getNotifyTypeHeader (h, data) {
                const col = this.AllNotifyTypeList[data.$index]
                if (col.type) {
                    return h('div', { 'class': 'notify-table-heder' }, [
                        h('img', { 'class': 'notify-icon', attrs: { src: `data:image/png;base64,${col.icon}` } }, []),
                        h('span', { style: 'word-break: break-all;' }, [col.label])
                    ])
                } else {
                    return h('span', {}, [col.text])
                }
            },
            onSelectNotifyType (row, type, val) {
                const data = this.selectNotifyType[row]
                if (val) {
                    data.push(type)
                } else {
                    const index = data.findIndex(item => item === type)
                    if (index > -1) {
                        data.splice(index, 1)
                    }
                }
                this.$emit('onSelectNotifyType', this.selectNotifyType)
            },
            onReceiverGroup (val) {
                this.$emit('onReceiverGroup', val)
            },
            async getProjectNotifyGroup () {
                try {
                    this.notifyGroupLoading = true
                    if (!this.projectBaseInfo.notify_group) {
                        const resp = await this.loadProjectBaseInfo()
                        this.setProjectBaseInfo(resp.data)
                    }
                    const res = await this.getNotifyGroup({ project_id: this.$route.params.project_id })
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
    }
    /deep/ .bk-checkbox-text {
        display: inline-flex;
        align-items: center;
        width: 100px;
    }
    .notify-type-table {
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
