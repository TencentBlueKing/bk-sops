class Node {
    static TYPE_ENUM = 1
    static TYPE_RANG = 2
    static TYPE_REPEAT = 3
    static TYPE_RANG_REPEAT = 4
    constructor ({
        type,
        value,
        min,
        max,
        repeatInterval
    }) {
        this.type = type
        this.value = value || ''
        this.min = min
        this.max = max
        this.repeatInterval = repeatInterval
    }
}

const fieldList = [
    'minute',
    'hour',
    'dayOfMonth',
    'month',
    'dayOfWeek'
]

// const preDefined = {
//     '@yearly': '每年',
//     '@monthly': '每月',
//     '@weekly': '每周',
//     '@daily': '每天',
//     '@hourly': '每小时'
// }
const weekDayMap = {
    0: '日',
    1: '一',
    2: '二',
    3: '三',
    4: '四',
    5: '五',
    6: '六',
    7: '日'
}
const weekDesDayMap = {
    sun: '日',
    mon: '一',
    tue: '二',
    wed: '三',
    thu: '四',
    fri: '五',
    sat: '六'
}

const getWeekDayValue = (value) => {
    if (weekDayMap[value]) {
        return weekDayMap[value]
    }
    const text = value.toString().toLowerCase()
    if (weekDesDayMap[text]) {
        return weekDesDayMap[text]
    }
    return value
}

const getHourValue = (value) => {
    const num = ~~value
    if (num < 5) {
        return `凌晨${num}点`
    }
    if (num < 12) {
        return `上午${num}点`
    }
    if (num === 12) {
        return `中午${num}点`
    }
    if (num < 18) {
        return `下午${num}点`
    }
    return `晚上${num}点`
}

const getMinuteValue = (value) => {
    const num = ~~value
    if (num < 10) {
        return `0${num}`
    }
    return num
}

const parsetext = (expression) => {
    const stack = []
    const rangReg = /-/
    const repeatReg = /\//
    const atoms = (`${expression}`).trim().split(',')
    let index = -1
    // eslint-disable-next-line no-plusplus
    while (++index < atoms.length) {
        const enumValue = atoms[index]
        if (rangReg.test(enumValue) && repeatReg.test(enumValue)) {
            // 在指定区间重复
            const [rang, repeatInterval] = enumValue.split('/')
            const [min, max] = rang.split('-')
            stack.push(new Node({
                type: Node.TYPE_RANG_REPEAT,
                min,
                max,
                repeatInterval
            }))
            continue
        } else if (repeatReg.test(enumValue)) {
            // 从指定起始位置重复
            const [value, repeatInterval] = enumValue.split('/')
            stack.push(new Node({
                type: Node.TYPE_REPEAT,
                value,
                repeatInterval
            }))
            continue
        } else if (rangReg.test(enumValue)) {
            // 指定区间
            const [min, max] = enumValue.split('-')
            stack.push(new Node({
                type: Node.TYPE_RANG,
                min,
                max
            }))
            continue
        } else {
            stack.push(new Node({
                type: Node.TYPE_ENUM,
                value: enumValue
            }))
        }
    }
    return stack
}

const optimze = (fieldMap) => {
    const isAllValue = node => node.length === 1
    && node[0].type === Node.TYPE_ENUM
    && (node[0].value === '*' || node[0].value === '?')
    const prettyMap = {}

    prettyMap.month = isAllValue(fieldMap.month) ? [] : fieldMap.month

    if (isAllValue(fieldMap.dayOfMonth) && isAllValue(fieldMap.month) && isAllValue(fieldMap.dayOfWeek)) {
        prettyMap.dayOfMonth = []
        delete prettyMap.month
    } else {
        if (!isAllValue(fieldMap.dayOfWeek)) {
            prettyMap.dayOfWeek = fieldMap.dayOfWeek
        }
        if (!isAllValue(fieldMap.dayOfMonth)) {
            prettyMap.dayOfMonth = fieldMap.dayOfMonth
        }
        if (!prettyMap.dayOfMonth && !prettyMap.dayOfWeek && prettyMap.month.length > 0) {
            prettyMap.dayOfMonth = []
        }
    }
    prettyMap.hour = isAllValue(fieldMap.hour) ? [] : fieldMap.hour
    if (prettyMap.hour.length < 1 && prettyMap.dayOfMonth && prettyMap.dayOfMonth.length < 1) {
        delete prettyMap.dayOfMonth
    }
    prettyMap.minute = isAllValue(fieldMap.minute) ? [] : fieldMap.minute
    if (prettyMap.minute.length < 1 && prettyMap.hour.length < 1) {
        delete prettyMap.hour
    }
    return prettyMap
}

const translateMap = {
    minute: {
        genAll: () => '每分钟',
        [Node.TYPE_ENUM]: node => `${getMinuteValue(node.value)}分`,
        [Node.TYPE_RANG]: node => `${getMinuteValue(node.min)}分到${getMinuteValue(node.max)}分`,
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return `每隔${node.repeatInterval}分钟`
            }
            return `从${getMinuteValue(node.value)}分开始每隔${node.repeatInterval}分钟`
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => `从${getMinuteValue(node.min)}分开始到${getMinuteValue(node.max)}分的每${node.repeatInterval}分钟`
    },
    hour: {
        genAll: () => '每小时',
        [Node.TYPE_ENUM]: node => `${getHourValue(node.value)}`,
        [Node.TYPE_RANG]: node => `${getHourValue(node.min)}到${getHourValue(node.max)}`,
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return `每隔${node.repeatInterval}个小时`
            }
            return `从${getHourValue(node.value)}开始每隔${node.repeatInterval}个小时`
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => `从${getHourValue(node.min)}开始到${getHourValue(node.max)}的每${node.repeatInterval}个小时`
    },
    dayOfMonth: {
        genAll: () => '每天',
        [Node.TYPE_ENUM]: node => `${node.value}号`,
        [Node.TYPE_RANG]: node => `${node.min}号到${node.max}号`,
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return `每隔${node.repeatInterval}天`
            }
            return `从${node.value}号开始每隔${node.repeatInterval}天`
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => `从${node.min}号开始到${node.max}号的每${node.repeatInterval}天`
    },
    month: {
        genAll: () => '每月',
        [Node.TYPE_ENUM]: node => `${node.value}月`,
        [Node.TYPE_RANG]: node => `${node.min}月到${node.max}月`,
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return `每隔${node.repeatInterval}个月`
            }
            return `从${node.value}月开始每隔${node.repeatInterval}个月`
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => `从${node.min}月开始到${node.max}月的每${node.repeatInterval}个月`
    },
    dayOfWeek: {
        genAll: () => '每天',
        [Node.TYPE_ENUM]: node => `每周${getWeekDayValue(node.value)}`,
        [Node.TYPE_RANG]: node => `每周${getWeekDayValue(node.min)}到周${getWeekDayValue(node.max)}`,
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return `每个星期内的每隔${node.repeatInterval}天`
            }
            return `从每周${getWeekDayValue(node.value)}开始每隔${node.repeatInterval}天`
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => `从每周${getWeekDayValue(node.min)}开始到周${getWeekDayValue(node.max)}的每隔${node.repeatInterval}天`
    }
}

const translateText = (ast) => {
    const concatTextNew = (ast, field) => {
        if (!Object.prototype.hasOwnProperty.call(ast, field)) {
            return ''
        }
        const sequence = ast[field]
        const translate = translateMap[field]
        if (sequence.length < 1) {
            return translate.genAll()
        }
        const stack = sequence.map(node => translate[node.type](node))
        if (stack.length < 2) {
            return stack.join('')
        }
        const pre = stack.slice(0, -1)
        const last = stack.slice(-1)
        return `${pre.join('，')}和${last[0]}`
    }
    return [
        concatTextNew(ast, 'month'),
        concatTextNew(ast, 'dayOfMonth'),
        concatTextNew(ast, 'dayOfWeek'),
        concatTextNew(ast, 'hour'),
        concatTextNew(ast, 'minute')
    ]
}

const print = (expression) => {
    const atoms = (`${expression}`).trim().split(/\s+/)
    const fieldMap = {}
    atoms.forEach((item, index) => {
        fieldMap[fieldList[index]] = parsetext(item)
    })
    const ast = optimze(fieldMap)
    return translateText(ast)
}

export default expression => print(expression)
