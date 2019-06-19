import bus from '@/utils/bus.js'

const permission = {
    methods: {
        /**
         * 判断当前权限是否满足需要的权限
         * @param {Array} reqPermission 需要的权限
         * @param {Array} curPermission 当前拥有的权限
         */
        hasPermission (reqPermission = [], curPermission = [], permissionMap = []) {
            return reqPermission.every(item => {
                if (curPermission.includes(item)) {
                    return true
                } else {
                    const perm = permissionMap.find(op => op.operate_id === item)
                    return perm.actions_id.every(p => curPermission.includes(p))
                }
            })
        },
        triggerPermisionModal (permissions) {
            bus.$emit('showPermissionModal', permissions)
        }
    }
}

export default permission
