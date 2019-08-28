<template>
    <div class="tag-button">
        <el-button
            v-if="title"
            :type="type"
            :size="size"
            :plain="plain"
            :circle="circle"
            :icon="icon"
            @click="onClick">
            {{ title }}
        </el-button>
        <el-button
            v-else
            :type="type"
            :size="size"
            :plain="plain"
            :circle="circle"
            :icon="icon"
            @click="onClick">
        </el-button>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'

    const buttonAttrs = {
        title: {
            type: String,
            required: false,
            default: '',
            description: 'determine whether it\'s a plain button'
        },
        type: {
            type: String,
            required: false,
            default: '',
            description: 'button type primary / success / warning / danger / info / text'
        },
        icon: {
            type: String,
            required: false,
            default: '',
            description: 'button type primary / success / warning / danger / info / text'
        },
        size: {
            type: String,
            required: false,
            default: 'mini',
            description: 'button size medium / small / mini'

        },
        plain: {
            type: Boolean,
            required: false,
            default: false,
            description: 'determine whether it\'s a plain button'
        },
        round: {
            type: Boolean,
            required: false,
            default: false,
            description: 'determine whether it\'s a round button'
        },
        circle: {
            type: Boolean,
            required: false,
            default: false,
            description: 'determine whether it\'s a circle button'
        }
    }
    export default {
        name: 'TagButton',
        mixins: [getFormMixins(buttonAttrs)],
        methods: {
            onClick () {
                this.emit_event(this.tagCode, 'click', this.value)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .tag-button {
        height: 36px;
        line-height: 36px;
    }
</style>
