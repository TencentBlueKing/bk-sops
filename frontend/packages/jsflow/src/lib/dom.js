/**
 * 目标 DOM 是否包含当前 DOM
 * @param {Object} root 目标 DOM 节点对象
 * @param {Object} el 当前 DOM 节点对象
 */

export function nodeContains (root, el) {
    if (root.compareDocumentPosition) {
        return root === el || !!(root.compareDocumentPosition(el) & 16)
    }
    if (root.contains && el.nodeType === 1) {
        return root.contains(el) && root !== el
    }
    while ((el = el.parentNode)) {
        if (el === root) return true
    }
    return false
}

/**
 * 节点及祖先节点是否包含传入的 class
 * 该方法暂支持 class 匹配
 *
 * @param {Object} el 当前 DOM 节点对象
 * @param {String} selector 选择器
 *
 * @return {NodeObject, Null} 节点对象或者null
 */
export function matchSelector (el, selector) {
    if (el.nodeType === 1 && el.classList.contains(selector)) {
        return el
    }
    if (el.parentNode.nodeName !== 'HTML') {
        return matchSelector(el.parentNode, selector)
    }
    return null
}
/**
 * 获取PC、移动端兼容的点击或触摸事件对象
 * @param {Object} event 事件对象
 */
export function getPolyfillEvent (event) {
    if ('touches' in event) {
        return event.touches[0]
    }
    return event
}
