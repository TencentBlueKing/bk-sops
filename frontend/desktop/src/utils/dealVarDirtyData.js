export default class DealVarDirtyData {
    constructor (constants = {}) {
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
        const constants = {}
        for (const [key, value] of Object.entries(this.constants)) {
            if (!this.illegalKeys.includes(key)) {
                constants[key] = value
            }
        }
        return constants
    }
}
