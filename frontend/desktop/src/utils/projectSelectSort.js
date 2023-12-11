const isLetterOrNumberReg = (str) => {
    return /^[0-9a-zA-Z]+$/.test(str)
}
const isAllChineseStr = (str) => {
    return /^[\u4E00-\u9FA5]+$/.test(str)
}
const splitStringByNumber = (str, sortByNumericalSize = false) => {
    let strArr = []
    const REG_STRING_NUMBER_PARTS = /\d+|\D+/g
    const arr = str.match(REG_STRING_NUMBER_PARTS)
    for (let i = 0; i < arr.length; i++) {
        const splitStr = arr[i]
        if (isNaN(splitStr)) {
            strArr = strArr.concat(splitStr.split(''))
        } else {
            // Whether to split numbers
            if (!sortByNumericalSize) {
                strArr = strArr.concat(splitStr.split(''))
            } else {
                strArr.push(splitStr)
            }
        }
    }
    return strArr
}
const compare = (a, b, sortByNumericalSize = true) => {
    // 都是数字或字母
    if (isLetterOrNumberReg(a) && isLetterOrNumberReg(b)) {
        return a.localeCompare(b, 'zh-Hans-CN', { numeric: true })
    }

    // 中文字符串自己比较
    if (isAllChineseStr(a) && isAllChineseStr(b)) {
        return a.localeCompare(b, 'zh-Hans-CN', { numeric: true })
    }

    const arrA = splitStringByNumber(a, sortByNumericalSize)
    const arrB = splitStringByNumber(b, sortByNumericalSize)

    let result = 0
    const length = Math.min(arrA.length, arrB.length)
    for (let i = 0; i < length; i++) {
        const charA = arrA[i]
        const charB = arrB[i]
        // 数字, 字符串排在 中文前面
        if (!isAllChineseStr(charA) && isAllChineseStr(charB)) {
            return -1
        }

        if (isAllChineseStr(charA) && !isAllChineseStr(charB)) {
            return 1
        }

        // 中文字符直接比较
        if (isAllChineseStr(charA) && isAllChineseStr(charB)) {
            result = charA.localeCompare(charB, 'zh-Hans-CN')
        } else {
            // 都不是中文
            result = charA.localeCompare(charB, 'zh-Hans-CN', { numeric: true })
        }

        if (result !== 0) {
            return result
        }
    }

    // result === 0;
    if (arrA.length > arrB.length) return 1
    if (arrA.length < arrB.length) return -1
    return 0
}

export default compare
