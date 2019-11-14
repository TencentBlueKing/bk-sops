import { errorHandler } from '@/utils/errorHandler.js'
import { mapActions } from 'vuex'
const task = {
    methods: {
        ...mapActions('task/', [
            'getInstanceStatus'
        ]),
        getExecuteStatus (list) {
            const statusList = list.map((item, index) => {
                const status = {}
                if (item.is_finished) {
                    status.cls = 'finished bk-icon icon-check-circle-shape'
                    status.text = gettext('完成')
                } else if (item.is_revoked) {
                    status.cls = 'revoke common-icon-dark-circle-shape'
                    status.text = gettext('撤销')
                } else if (item.is_started) {
                    status.cls = 'loading common-icon-loading'
                    this.getExecuteDetail(statusList, item, index)
                } else {
                    status.cls = 'created common-icon-dark-circle-shape'
                    status.text = gettext('未执行')
                }
                return status
            })
            return statusList
        },
        async getExecuteDetail (statusList, item, index) {
            const data = {
                instance_id: task.id,
                project_id: task.project.id
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
                    statusList.splice(index, 1, status)
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
