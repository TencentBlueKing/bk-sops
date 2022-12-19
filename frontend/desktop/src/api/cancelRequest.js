import axios from 'axios'

class CancelRequest {
    sourceMap = {}
    initSourceMap () {
        this.sourceMap = {}
    }
    updateSourceMap (type = 'default') {
        if (this.sourceMap[type]) {
            this.sourceMap[type].cancel('cancelled')
        }
        this.sourceMap[type] = axios.CancelToken.source()
    }
    getToken (type = 'default') {
        return this.sourceMap[type].token
    }
}

export default CancelRequest
