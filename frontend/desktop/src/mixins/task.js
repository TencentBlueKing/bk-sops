import { errorHandler } from '@/utils/errorHandler.js'
import { mapActions } from 'vuex'
const task = {
    methods: {
        ...mapActions('task/', [
            'getInstanceStatus'
        ]),
        /**
         * getExecuteStatus
         * @description
         * acceptVarName 为了可以异步改变数据源
         * @param {String} acceptVarName 已定义的状态变量
         * @param {Array} list 源 task 数据
         */
        getExecuteStatus (acceptVarName, list) {
            this[acceptVarName] = list.map((item, index) => {
                const status = {}
                if (item.is_finished) {
                    status.cls = 'finished bk-icon icon-check-circle-shape'
                    status.text = gettext('完成')
                } else if (item.is_revoked) {
                    status.cls = 'revoke common-icon-dark-circle-shape'
                    status.text = gettext('撤销')
                } else if (item.is_started) {
                    status.cls = 'loading common-icon-loading'
                    this.getExecuteDetail(acceptVarName, item, index)
                } else {
                    status.cls = 'created common-icon-dark-circle-shape'
                    status.text = gettext('未执行')
                }
                return status
            })
        },
        async getExecuteDetail (acceptVarName, item, index) {
            const data = {
                instance_id: item.id,
                project_id: item.project.id
            }
            try {
                const detailInfo = await this.getInstanceStatus(data)
                if (detailInfo.result) {
                    const state = detailInfo.data.state
                    const status = {}
                    switch (state) {
                        case 'RUNNING':
                        case 'BLOCKED':
                            status.cls = 'running common-icon-dark-circle-ellipsis'
                            status.text = gettext('执行中')
                            break
                        case 'SUSPENDED':
                            status.cls = 'execute common-icon-dark-circle-pause'
                            status.text = gettext('暂停')
                            break
                        case 'NODE_SUSPENDED':
                            status.cls = 'execute'
                            status.text = gettext('节点暂停')
                            break
                        case 'FAILED':
                            status.cls = 'failed common-icon-dark-circle-close'
                            status.text = gettext('失败')
                            break
                        default:
                            status.text = gettext('未知')
                    }
                    this[acceptVarName].splice(index, 1, status)
                } else {
                    errorHandler(detailInfo, this)
                }
            } catch (e) {
                errorHandler(e, this)
            }
        }

    }
}

export default task
