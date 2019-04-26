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
 * @param {String} el 当前节点
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
