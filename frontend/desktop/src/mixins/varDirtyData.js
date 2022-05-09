import tools from '@/utils/tools.js'
import { mapState, mapMutations } from 'vuex'
const varDirtyData = {
    data () {
        return {
            illegalKeys: [] // 不合规的变量key值
        }
    },
    computed: {
        ...mapState({
            'constants': state => state.template.constants
        })
    },
    methods: {
        ...mapMutations('template/', [
            'setConstants'
        ]),
        checkVarDirtyData () {
            const variableKeys = Object.keys(this.constants)
            const illegalKeys = []
            variableKeys.forEach(key => {
                if (/(^\${(_env_|_system\.))|(^(_env_|_system\.))/.test(key)) {
                    illegalKeys.push(key)
                }
            })
            if (illegalKeys.length) {
                this.illegalKeys = illegalKeys
                this.isVarKeysDialogShow = true
                return true
            }
            return false
        },
        clearVarDirtyData () {
            const constants = tools.deepClone(this.constants)
            this.illegalKeys.forEach(key => {
                this.$delete(constants, key)
            })
            this.setConstants(constants)
        }
    }
}
export default varDirtyData
