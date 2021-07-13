import bus from '@/utils/bus.js'
const permission = {
    methods: {
        /**
         * 判断当前权限是否满足需要的权限
         * @param {Array} reqPermission 需要申请的权限
         * @param {Array} curPermission 当前拥有的权限
         */
        hasPermission (reqPermission = [], curPermission = []) {
            const { actions } = this.$store.state.permissionMeta
            return reqPermission.every((item) => {
                const permActionData = actions.find(action => action.id === item)
                if (!permActionData) { // 权限没有在 meta 数据中返回，判定为无对应权限
                    return false
                }
                if (!curPermission.includes(item)) {
                    return false
                }
                if (permActionData.relate_actions.length > 0) {
                    return this.hasPermission(permActionData.relate_actions, curPermission)
                }
                return true
            })
        },
        /**
         * 拼接申请权限跳转链接接口请求参数
         * @param {Array} reqPermission 需要的申请的权限
         * @param {Array} curPermission 当前拥有的权限
         * @param {Array} resourceData 资源数据
         */
        applyForPermission (reqPermission = [], curPermission = [], resourceData = {}) {
            const { actions, resources, system } = this.$store.state.permissionMeta
            const bksops = system.find(item => item.id === 'bk_sops')
            const { id: systemId, name: systemName } = bksops
            const actionsData = this.assembleActionsData(reqPermission, curPermission, resourceData, actions, resources, systemId, systemName)

            const data = {
                system_id: systemId,
                system_name: systemName,
                actions: actionsData
            }
            this.triggerPermisionModal(data)
        },
        /**
         * 组装 actions 数据，权限之间可能有相互依赖关系需要递归处理
         * @param {Arrau} reqPermission 需要的申请的权限
         * @param {Array} curPermission 当前拥有的权限
         * @param {Object} resourceData 资源实例数据
         * @param {Array} actions 系统中所有需要鉴权的操作相关信息
         * @param {Array} resources 系统中资源信息
         * @param {String} systemId 系统 id
         * @param {String} systemName 系统名称
         */
        assembleActionsData (reqPermission, curPermission, resourceData, actions, resources, systemId, systemName) {
            const actionsData = []
            reqPermission.forEach((requiredItem) => {
                const permActionData = actions.find(action => action.id === requiredItem)
                // 权限字典里不存在该权限时
                if (!permActionData) {
                    return
                }
                // 用户没有该权限
                if (!curPermission.includes(requiredItem)) {
                    const relateResources = []
                    permActionData.relate_resources.forEach((reItem) => {
                        const resourceMap = resources.find(item => item.id === reItem)
                        const instances = this.assembleInstances(resources, resourceMap, resourceData)
                        relateResources.push({
                            system_id: systemId,
                            system_name: systemName,
                            type: resourceMap.id,
                            type_name: resourceMap.name,
                            instances: [instances]
                        })
                    })
                    actionsData.push({
                        id: permActionData.id,
                        name: permActionData.name,
                        related_resource_types: relateResources
                    })
                }
                // 该权限依赖其他权限
                if (permActionData.relate_actions.length > 0) {
                    const relateActions = this.assembleActionsData(
                        permActionData.relate_actions,
                        curPermission,
                        resourceData,
                        actions,
                        resources,
                        systemId,
                        systemName
                    )
                    relateActions.forEach((item) => {
                        if (actionsData.findIndex(action => action.id === item.id) === -1) { // 避免操作权限重复
                            actionsData.push(item)
                        }
                    })
                }
            })
            return actionsData
        },
        /**
         * 拼接权限所关联的资源实例信息
         * @param {Object} resources 系统中资源信息
         * @param {Object} resourceMap 当前资源详情
         * @param {Object} resourceData 资源实例数据
         */
        assembleInstances (resources, resourceMap, resourceData) {
            let data = []
            if (resourceMap.parent_id) {
                const parentMap = resources.find(item => item.id === resourceMap.parent_id)
                data = data.concat(this.assembleInstances(resources, parentMap, resourceData))
            }
            const instanceData = resourceData[resourceMap.id]
            instanceData.forEach((item) => {
                data.push({
                    type: resourceMap.id,
                    type_name: resourceMap.name,
                    id: Number(item.id),
                    name: item.name
                })
            })
            return data
        },
        /**
         * 打开权限申请弹窗
         * @param {Obejct} permissions 无权限请求权限中心链接请求参数数据
         */
        triggerPermisionModal (permissions) {
            bus.$emit('showPermissionModal', permissions)
        }
    }
}

export default permission
