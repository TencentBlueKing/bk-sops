/**
 * 获取"我创建的"筛选条件的 values
 * 多租户下返回 { id, name } 对象以正确展示 display_name；非多租户返回纯 username 字符串
 * @param {String} username 当前用户的 username
 * @param {Array} searchSelectValue 当前已选中的搜索条件
 * @param {Array} searchList 搜索条件列表定义
 * @returns {Object} info 搜索条件对象
 */
export function getMyCreateFilterInfo (username, searchSelectValue, searchList) {
    const userValue = window.ENABLE_MULTI_TENANT_MODE
        ? { id: username, name: window.DISPLAY_NAME || username }
        : username
    const creatorInfo = searchSelectValue.find(item => item.id === 'creator')
    let info = {}
    if (creatorInfo) {
        creatorInfo.values = [userValue]
        info = creatorInfo
    } else {
        const form = searchList.find(item => item.id === 'creator')
        info = { ...form, values: [userValue] }
        searchSelectValue.push(info)
    }
    return info
}
