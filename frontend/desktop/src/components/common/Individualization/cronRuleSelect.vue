<template>
    <div class="cron-sops"
        :class="[
            { 'is-error': isError },
            `error-${errorField}`,
            `select-${selectIndex}`
        ]">
        <div class="time-describe">
            <span class="time-text minute" @click="handleTimeTextChange('minute')">{{ $t('分') }}</span>
            <span class="time-text hour" @click="handleTimeTextChange('hour')">{{ $t('时') }}</span>
            <span class="time-text dayOfMonth" @click="handleTimeTextChange('dayOfMonth')">{{ $t('日') }}</span>
            <span class="time-text month" @click="handleTimeTextChange('month')">{{ $t('月') }}</span>
            <span class="time-text dayOfWeek" @click="handleTimeTextChange('dayOfWeek')">{{ $t('周') }}</span>
        </div>
        <i class="common-icon-info rule-tips" v-bk-tooltips="ruleTipsHtmlConfig"></i>
        <!-- corn 规则 tips -->
        <div id="periodic-cron-tips-html">
            <img style="width:100%" class="ui-img" :src="periodicCronImg">
        </div>
        <div class="time-input">
            <input
                ref="input"
                class="input"
                type="text"
                :value="nativeValue"
                @input="handleInput"
                @blur="handleBlur"
                @keyup.left="handleSelectText"
                @keyup.right="handleSelectText"
                @mousedown="handleSelectText">
        </div>
        <div class="error-msg" v-if="isError">
            {{ value.length - 4 > 100 ? $t('长度超过100个字符，请修改规则') : $t('使用了除“,-*/”以外的特殊字符，请修改规则') }}
        </div>
        <div class="time-parse" v-if="parseValue.length > 1">
            <template v-if="parseValue[0]">
                <span class="month">{{ parseValue[0] }}</span>
            </template>
            <template v-if="parseValue[1]">
                <span class="dayOfMonth">{{ parseValue[1] }}</span>
                <span v-if="parseValue[2]">{{ $t('以及当月') }}</span>
            </template>
            <template v-if="parseValue[2]">
                <span class="dayOfWeek">{{ parseValue[2] }}</span>
            </template>
            <template v-if="parseValue[3]">
                <span class="hour">{{ parseValue[3] }}</span>
            </template>
            <span class="minute">{{ parseValue[4] }}</span>
        </div>
        <div v-if="nextTime.length > 0" class="time-next" :class="{ active: isTimeMore }">
            <div class="label">{{ $t('下次：') }}</div>
            <div class="value">
                <div v-for="(time, index) in nextTime" :key="`${time}_${index}`">{{ time }}</div>
            </div>
            <div class="arrow" @click="handleShowMore">
                <i class="bk-icon icon-angle-double-down arrow-button"></i>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import CronExpression from 'cron-parser-custom'
    import Translate from '@/utils/cron.js'
    import tools from '@/utils/tools.js'
    const labelIndexMap = {
        minute: 0,
        hour: 1,
        dayOfMonth: 2,
        month: 3,
        dayOfWeek: 4,
        0: 'minute',
        1: 'hour',
        2: 'dayOfMonth',
        3: 'month',
        4: 'dayOfWeek'
    }
    export default {
        name: '',
        props: {
            value: {
                type: String,
                default: '*/5 * * * *'
            }
        },
        data () {
            return {
                selectIndex: '',
                nativeValue: this.value,
                nextTime: [],
                parseValue: [],
                errorField: '',
                isError: false,
                isTimeMore: false,
                periodicCronImg: require('@/assets/images/' + i18n.t('task-zh') + '.png'),
                ruleTipsHtmlConfig: {
                    allowHtml: true,
                    width: 560,
                    trigger: 'mouseenter',
                    theme: 'light',
                    content: '#periodic-cron-tips-html',
                    placement: 'top-start'
                }
            }
        },
        watch: {
            nativeValue (val) {
                // 长度超过100个字符
                if (val.length > 100) {
                    this.parseValue = []
                    this.nextTime = []
                    this.isError = true
                }
            }
        },
        mounted () {
            if (!this.nativeValue) {
                return
            }
            this.checkAndTranslate(this.nativeValue)
        },
        methods: {
            /**
             * @desc 检测crontab格式和翻译
             */
            checkAndTranslate (value) {
                const interval = CronExpression.parse(`0 ${value.trim()}`, {
                    currentDate: new Date()
                })
                let i = 5
                this.nextTime = []
                while (i > 0) {
                    this.nextTime.push(tools.prettyDateTimeFormat(interval.next().toString()))
                    i -= 1
                }
                this.errorField = ''
                this.isError = false
                this.parseValue = Translate(value)
            },
            /**
             * @desc 选中crontab字段
             * @param {String} lable 选中的字段名
             */
            handleTimeTextChange (label) {
                if (!this.nativeValue) {
                    return
                }
                const timeItem = this.nativeValue.split(' ')
                const index = labelIndexMap[label]
                if (timeItem.length < index) {
                    return
                }
                const preStrLength = timeItem.slice(0, index).join('').length + index
                const endPosition = preStrLength + timeItem[index].length
                setTimeout(() => {
                    this.selectIndex = label
                    this.$refs.input.focus()
                    this.$refs.input.selectionStart = preStrLength
                    this.$refs.input.selectionEnd = endPosition
                })
            },
            /**
             * @desc 输入框失去焦点
             */
            handleBlur () {
                this.selectIndex = ''
            },
            /**
             * @desc 选中输入框文本
             * @param {Object} event 文本选择事件
             */
            handleSelectText (event) {
                const $target = event.target
                const value = $target.value.trim()
                this.nativeValue = value
                if (!value) return
                setTimeout(() => {
                    const cursorStart = $target.selectionStart
                    const cursorStr = value.slice(0, cursorStart)
                    const checkBackspce = cursorStr.match(/ /g)
                    if (checkBackspce) {
                        this.selectIndex = labelIndexMap[checkBackspce.length]
                    } else {
                        this.selectIndex = labelIndexMap['0']
                    }
                })
            },
            /**
             * @desc 输入框输入
             * @param {Object} event 输入框input事件
             */
            handleInput: tools.debounce(function (event) {
                const { value } = event.target
                this.nativeValue = value
                try {
                    this.checkAndTranslate(value)
                    this.$emit('change', value)
                    this.$emit('input', value)
                } catch (error) {
                    this.parseValue = []
                    this.nextTime = []
                    const all = [
                        'minute',
                        'hour',
                        'dayOfMonth',
                        'month',
                        'dayOfWeek'
                    ]
                    if (all.includes(error.message)) {
                        this.errorField = error.message
                    }
                    this.isError = true
                    this.$emit('change', '')
                    this.$emit('input', '')
                }
            }, 200),
            /**
             * @desc 展示下次执行时间列表
             */
            handleShowMore () {
                this.isTimeMore = !this.isTimeMore
            }
        }
    }
</script>
<style lang='scss'>
    .cron-sops {
        background: #f0f1f5;
        &.is-error {
            .time-input {
                .input {
                    border-color: #ff5656;
                }
            }
        }
        /* stylelint-disable selector-class-pattern */
        &.error-month .month,
        &.error-dayOfMonth .dayOfMonth,
        &.error-dayOfWeek .dayOfWeek,
        &.error-hour .hour,
        &.error-minute .minute {
            color: #ff5656 !important;
        }
        &.select-month .month,
        &.select-dayOfMonth .dayOfMonth,
        &.select-dayOfWeek .dayOfWeek,
        &.select-hour .hour,
        &.select-minute .minute {
            color: #3a84ff;
        }
        .time-describe {
            display: flex;
            justify-content: center;
        }
        .time-text {
            padding: 0 19px;
            font-size: 12px;
            line-height: 22px;
            color: #c4c6cc;
            cursor: pointer;
            transition: all 0.1s;
            &.active {
                color: #3a84ff;
            }
            &.field-error {
                color: #ff5656;
            }
        }
        .time-input {
            .input {
                width: 100%;
                height: 48px;
                padding: 0 30px;
                font-size: 24px;
                line-height: 48px;
                word-spacing: 30px;
                color: #63656e;
                text-align: center;
                border: 1px solid #3a84ff;
                border-radius: 2px;
                outline: none;
                &::selection {
                    color: #3a84ff;
                    background: transparent;
                }
            }
        }
        .error-msg {
            font-size: 12px;
            color: #ea3636;
            line-height: 18px;
            text-align: center;
            margin-top: 12px;
        }
        .time-parse {
            font-size: 12px;
            padding: 10px 0;
            margin-top: 8px;
            line-height: 18px;
            color: #63656e;
            text-align: center;
        }
        .time-next {
            display: flex;
            height: 18px;
            overflow: hidden;
            font-size: 12px;
            line-height: 18px;
            color: #979ba5;
            text-align: center;
            transition: height 0.2s linear;
            align-content: center;
            justify-content: center;
            &.active {
                height: 90px;
                .arrow {
                    align-items: flex-end;
                    .arrow-button {
                        transform: rotateZ(-180deg);
                    }
                }
            }
            .value {
                text-align: left;
            }
            .arrow {
                display: flex;
                padding-top: 2px;
                padding-bottom: 2px;
                padding-left: 2px;
                font-size: 12px;
                cursor: pointer;
            }
            .arrow-button {
                font-size: 18px;
                margin-top: -2px;
            }
        }
        .rule-tips {
            position: absolute;
            top: 20px;
            right: 20px;
            color: #979ba5;
            font-size: 14px;
        }
    }
</style>
