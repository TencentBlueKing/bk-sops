import bus from '@/utils/bus.js'

const permission = {
    methods: {
        /**
         * 判断当前权限是否满足需要的权限
         * @param {Array} reqPermission 需要的权限
         * @param {Array} curPermission 当前拥有的权限
         * @param {Array} authOperations 权限字典
         */
        hasPermission (reqPermission = [], curPermission = [], authOperations = []) {
            return reqPermission.every(item => {
                const perm = authOperations.find(op => op.operate_id === item)
                if (!perm) {
                    return false
                }
                return perm.actions_id.every(p => curPermission.includes(p))
            })
        },
        /**
         * 申请权限
         * @param {Array} required 需要的申请的权限
         * @param {Object} resourceData 资源数据
         * @param {Array} authOperations 权限字典
         * @param {Object} authResource 资源信息
         */
        applyForPermission (required, resourceData, authOperations, authResource) {
            const actions = []
            authOperations.filter(item => {
                return required.includes(item.operate_id)
            }).forEach(perm => {
                perm.actions.forEach(action => {
                    if (!resourceData.auth_actions.includes(action.id)
                        && !actions.find(item => action.id === item.id)
                    ) {
                        actions.push(action)
                    }
                })
            })
            
            const { scope_id, scope_name, scope_type, system_id, system_name, resource, scope_type_name } = authResource
            const permissions = []
            actions.forEach(item => {
                const res = []
                if (resource.resource_type !== 'project' || item.id !== 'create') { // 创建项目权限不需要资源信息
                    res.push([{
                        resource_id: resourceData.id,
                        resource_name: resourceData.name,
                        resource_type: resource.resource_type,
                        resource_type_name: resource.resource_type_name
                    }])
                }
                
                permissions.push({
                    scope_id,
                    scope_name,
                    scope_type_name,
                    resource_type: resource.resource_type,
                    resource_type_name: resource.resource_type_name,
                    scope_type,
                    system_id,
                    system_name,
                    resources: res,
                    action_id: item.id,
                    action_name: item.name
                })
            })

            this.triggerPermisionModal(permissions)
        },
        triggerPermisionModal (permissions) {
            bus.$emit('showPermissionModal', permissions)
        }
    }
}

export default permission
