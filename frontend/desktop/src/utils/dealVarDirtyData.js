import tools from '@/utils/tools.js'
export default class DealVarDirtyData {
    constructor (constants) {
        this.constants = Object.assign({}, constants)
        this.illegalKeys = []
    }
    checkKeys () {
        const variableKeys = Object.keys(this.constants)
        const illegalKeys = []
        variableKeys.forEach(key => {
            if (/(^\${(_env_|_system\.))|(^(_env_|_system\.))/.test(key)) {
                illegalKeys.push(key)
            }
        })
        this.illegalKeys = illegalKeys
        return illegalKeys
    }
    handleIllegalKeys () {
        const constants = tools.deepClone(this.constants)
        this.illegalKeys.forEach(key => {
            this.$delete(constants, key)
        })
        return constants
    }
    static getInstance (constants) { // 共享实例
        if (!this.instance) {
            this.instance = new DealVarDirtyData(constants)
        }
        return this.instance
    }
}
