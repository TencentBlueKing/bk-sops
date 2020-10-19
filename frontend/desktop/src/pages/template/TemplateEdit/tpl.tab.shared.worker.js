const tabDict = {}
self.onconnect = function(e) {
    var port = e.ports[0]
    port.onmessage = function(message) {
        const { user, type, id, tpl } = message.data
        if (type === 'tplEditTabCountAdd') {
            if (!(user in tabDict)) {
                tabDict[user] = {}
            }
            if (!(id in tabDict[user])) {
                tabDict[user][id] = {}
            }
            if (!(tpl in tabDict[user][id])) {
                tabDict[user][id][tpl] = 0
            }
            tabDict[user][id][tpl] += 1
        } else if (type === 'tplEditTabCountDel') {
            tabDict[user][id][tpl] -= 1
            if (tabDict[user][id][tpl] === 0) {
                delete tabDict[user][id][tpl]
            }
        } else if (type === 'getTabDict') {
            port.postMessage(tabDict)
        }
    }
    port.start()
}
