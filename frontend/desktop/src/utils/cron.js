import i18n from '@/config/i18n/index.js'
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
    return i18n.t(`周${value}`)
}

const getHourValue = (value) => {
    const num = ~~value
    if (num < 5) {
        return i18n.t('凌晨{num}点', { num })
    }
    if (num < 12) {
        return i18n.t('上午{num}点', { num })
    }
    if (num === 12) {
        return i18n.t('中午{num}点', { num })
    }
    if (num < 18) {
        return i18n.t('下午{num}点', { num })
    }
    return i18n.t('晚上{num}点', { num })
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
        genAll: () => i18n.t('每分钟'),
        [Node.TYPE_ENUM]: node => textI18n('{0}分', [getMinuteValue(node.value)]),
        [Node.TYPE_RANG]: node => textI18n('{0}分到{1}分', [getMinuteValue(node.min), getMinuteValue(node.max)]),
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return textI18n('每隔{0}分钟', [node.repeatInterval])
            }
            return textI18n('从{0}分开始每隔{1}分钟', [node.value, node.repeatInterval])
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => textI18n('从{0}分开始到{1}分的每{2}分钟', [node.min, getMinuteValue(node.max), node.repeatInterval])
    },
    hour: {
        genAll: () => i18n.t('每小时'),
        [Node.TYPE_ENUM]: node => `${getHourValue(node.value)}`,
        [Node.TYPE_RANG]: node => textI18n('{0}到{1}', [getHourValue(node.min), getHourValue(node.max)]),
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return textI18n('每隔{0}个小时', [node.repeatInterval])
            }
            return textI18n('从{0}开始每隔{1}个小时', [getHourValue(node.value), node.repeatInterval])
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => textI18n('从{0}开始到{1}的每{2}个小时', [getHourValue(node.min), getHourValue(node.max), node.repeatInterval])
    },
    dayOfMonth: {
        genAll: () => i18n.t('每天'),
        [Node.TYPE_ENUM]: node => textI18n('{0}号', [node.value]),
        [Node.TYPE_RANG]: node => textI18n('{0}号到{2}号', [node.min, node.max]),
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return textI18n('每隔{0}天', [node.repeatInterval])
            }
            return textI18n('从{0}号开始每隔{1}天', [node.value, node.repeatInterval])
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => textI18n('从{0}号开始到{1}号的每{2}天', [node.min, node.max, node.repeatInterval])
    },
    month: {
        genAll: () => i18n.t('每月'),
        [Node.TYPE_ENUM]: node => textI18n('{0}月', [node.value]),
        [Node.TYPE_RANG]: node => textI18n('{0}月到{1}月', [node.min, node.max]),
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return textI18n('每隔{0}个月', [node.repeatInterval])
            }
            return textI18n('从{0}月开始每隔{1}个月', [node.value, node.repeatInterval])
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => textI18n('从{0}月开始到{1}月的每{2}个月', [node.min, node.max, node.repeatInterval])
    },
    dayOfWeek: {
        genAll: () => i18n.t('每天'),
        [Node.TYPE_ENUM]: node => textI18n('每{0}', [getWeekDayValue(node.value)]),
        [Node.TYPE_RANG]: node => textI18n('每{0}到{1}', [getWeekDayValue(node.min), getWeekDayValue(node.max)]),
        [Node.TYPE_REPEAT]: (node) => {
            if (node.value === '*') {
                return textI18n('每个星期内的每隔{0}天', [node.repeatInterval])
            }
            return textI18n('从每{0}开始每隔{1}天', [getWeekDayValue(node.value), node.repeatInterval])
        },
        // eslint-disable-next-line max-len
        [Node.TYPE_RANG_REPEAT]: node => textI18n('从每{0}开始到{1}的每隔{2}天', [getWeekDayValue(node.min), getWeekDayValue(node.max), node.repeatInterval])
    }
}

const textI18n = (str, fields) => {
    const xxx = fields.reduce((acc, cur, index) => {
        acc[index] = cur
        return acc
    }, {})
    return i18n.t(str, xxx)
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
        return textI18n('{0}和{1}', [pre.join('，'), last[0]])
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
