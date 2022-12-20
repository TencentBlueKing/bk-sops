import axios from 'axios'

class CancelRequest {
    static sourceMap = {}
  
    static cancelAll () {
        Object.keys(CancelRequest.sourceMap).forEach(type => {
            CancelRequest.sourceMap[type].cancel()
        })
    }
  
    static clearAll () {
        Object.keys(CancelRequest.sourceMap).forEach(type => {
            delete CancelRequest.sourceMap[type]
        })
    }
  
    constructor (type = 'default') {
        this.type = type
        this.cancel()
        CancelRequest.sourceMap[type] = axios.CancelToken.source()
    }
  
    cancel () {
        CancelRequest.sourceMap[this.type] && CancelRequest.sourceMap[this.type].cancel('cancelled')
    }
  
    clear () {
        delete CancelRequest.sourceMap[this.type]
    }
  
    get token () {
        return CancelRequest.sourceMap[this.type]?.token
    }
}

export default CancelRequest
