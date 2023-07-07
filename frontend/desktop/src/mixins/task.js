import { mapActions } from 'vuex'
import i18n from '@/config/i18n/index.js'

const task = {
    methods: {
        ...mapActions('task/', [
            'getTaskStatus'
        ]),
        /**
         * getExecuteStatus
         * @description
         * acceptVarName 为了可以异步改变数据源
         * @param {String} acceptVarName 已定义的状态变量
         * @param {Array} list 源 task 数据
         */
        getExecuteStatus (acceptVarName, list) {
            const statusMap = {}
            list.map((item) => {
                const status = {}
                if (item.is_expired) {
                    status.cls = 'expired bk-icon icon-clock-shape'
                    status.text = i18n.t('已过期')
                } else if (item.is_finished) {
                    status.cls = 'finished bk-icon icon-check-circle-shape'
                    status.text = i18n.t('完成')
                } else if (item.is_revoked) {
                    status.cls = 'revoke common-icon-dark-stop'
                    status.text = i18n.t('终止')
                } else if (item.is_started) {
                    status.cls = 'loading common-icon-loading'
                    this.getExecuteDetail(acceptVarName, item)
                } else {
                    status.cls = 'created common-icon-waitting'
                    status.text = i18n.t('未执行')
                }
                statusMap[item.id] = status
            })
            this[acceptVarName] = Object.assign({}, this[acceptVarName], statusMap)
        },
        async getExecuteDetail (acceptVarName, item) {
            const data = {
                instance_id: item.id,
                project_id: item.project.id
            }
            try {
                const detailInfo = await this.getTaskStatus(data)
                if (detailInfo.result) {
                    const { state } = detailInfo.data
                    const status = {}
                    switch (state) {
                        case 'RUNNING':
                        case 'BLOCKED':
                            status.cls = 'running common-icon-dark-circle-ellipsis'
                            status.text = i18n.t('执行中')
                            break
                        case 'READY':
                            status.cls = 'running common-icon-dark-circle-ellipsis'
                            status.text = i18n.t('排队中')
                            break
                        case 'SUSPENDED':
                            status.cls = 'execute common-icon-dark-circle-pause'
                            status.text = i18n.t('已暂停')
                            break
                        case 'NODE_SUSPENDED':
                            status.cls = 'execute'
                            status.text = i18n.t('节点暂停')
                            break
                        case 'FAILED':
                            status.cls = 'failed common-icon-dark-circle-close'
                            status.text = i18n.t('失败')
                            break
                        default:
                            status.text = i18n.t('未知')
                    }
                    this[acceptVarName][item.id] = status
                }
            } catch (e) {
                console.log(e)
            }
        }

    }
}

export default task
