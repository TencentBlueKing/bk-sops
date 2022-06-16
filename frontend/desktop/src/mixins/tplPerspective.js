import { mapState, mapActions } from 'vuex'

const tplPerspective = {
    data () {
        return {
            isPerspective: false, // 重复透视时只调一次接口
            nodeVariableInfo: {} // 节点输入输出变量
        }
    },
    computed: {
        ...mapState({
            'activities': state => state.template.activities,
            'constants': state => state.template.constants,
            'gateways': state => state.template.gateways,
            'internalVariable': state => state.template.internalVariable,
            'templateId': state => state.template.template_id
        })
    },
    methods: {
        ...mapActions('template/', [
            'getVariableCite',
            'loadInternalVariable'
        ]),
        ...mapActions('project/', [
            'loadEnvVariableList'
        ]),
        /**
         * 加载系统内置变量
         */
        async getSystemVars () {
            try {
                const result = await this.loadInternalVariable()
                const variableIndex = Object.keys(result.data).map(index => {
                    return result.data[index].index
                })
                let variableMinIndex = Math.min(...variableIndex)
                let internalVariable = { ...result.data }
                if (!this.common) {
                    const resp = await this.loadEnvVariableList({ project_id: this.$route.params.project_id })
                    const envVariableData = {}
                    Object.keys(resp.data).forEach(item => {
                        const { name, value, desc } = resp.data[item]
                        const projectVar = {
                            key: '${_env_' + resp.data[item].key + '}',
                            name,
                            value,
                            desc,
                            index: --variableMinIndex,
                            custom_type: 'input',
                            form_schema: {},
                            show_type: 'hide',
                            validation: '^.+$',
                            source_info: {},
                            source_type: 'project',
                            source_tag: 'input.input'
                        }
                        envVariableData['${_env_' + resp.data[item].key + '}'] = projectVar
                    })
                    internalVariable = Object.assign(envVariableData, result.data)
                }
                return internalVariable
            } catch (e) {
                console.log(e)
            }
        },
        async onTogglePerspective (val) {
            if (!val || this.isPerspective) return
            this.isPerspective = true
            // 已加载系统变量，直接取缓存
            let internalVariable = { ...this.internalVariable }
            if (!Object.keys(this.internalVariable).length) {
                internalVariable = await this.getSystemVars()
            }
            // 获取节点与变量的依赖关系
            try {
                const { activities, gateways, constants } = this.templateId ? this : this.previewData
                const variableList = { ...constants, ...internalVariable }
                const data = {
                    activities,
                    gateways,
                    constants: variableList
                }
                const resp = await this.getVariableCite(data)
                if (!resp.result) return
                const variableCited = resp.data.defined
                const nodeCitedInfo = Object.keys(variableCited).reduce((acc, key) => {
                    const values = variableCited[key]
                    const nodeInfo = variableList[key]
                    if (nodeInfo.source_type === 'component_outputs') {
                        const outputIds = Object.keys(nodeInfo.source_info) || []
                        outputIds.forEach(nodeId => {
                            if (!(nodeId in acc)) {
                                acc[nodeId] = {
                                    'input': [],
                                    'output': []
                                }
                            }
                            acc[nodeId]['output'].push(key)
                        })
                    } else {
                        values.activities.forEach(nodeId => {
                            if (!(nodeId in acc)) {
                                acc[nodeId] = {
                                    'input': [],
                                    'output': []
                                }
                            }
                            acc[nodeId]['input'].push(key)
                        })
                    }
                    return acc
                }, {})
                // 去重
                Object.keys(nodeCitedInfo).forEach(key => {
                    const values = nodeCitedInfo[key]
                    values.input = [...new Set(values.input)]
                    values.output = [...new Set(values.output)]
                })
                this.nodeVariableInfo = nodeCitedInfo
            } catch (e) {
                console.log(e)
            }
        }
    }
}

export default tplPerspective
