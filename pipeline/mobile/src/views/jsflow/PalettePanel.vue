<template>
    <div class="palette-panel">
        <slot name="palette">
            <ul class="palette-group">
                <li>
                    <div class="palette-item type-a">start</div>
                </li>
                <li>
                    <div class="palette-item type-b">end</div>
                </li>
                <li>
                    <div class="palette-item type-c">C</div>
                </li>
                <li>
                    <div class="palette-item type-d">D</div>
                </li>
            </ul>
        </slot>
    </div>
</template>
<script>
    export default {
        name: 'PalettePanel',
        // eslint-disable-next-line vue/require-prop-types
        props: ['selector'],
        data () {
            return {}
        },
        mounted () {
            this.$emit('registerPaletteEvent')
        }
    }
</script>
<style lang="scss">
    .palette-group {
        margin: 0;
        padding: 0;
        background: #fcfcfc;
        text-align: center;
        list-style: none;

        & > li {
            padding: 14px 0;
        }
    }

    .palette-item {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        font-size: 12px;
        color: #888888;
        border: 1px solid #999999;
        border-radius: 2px;
        cursor: pointer;
        user-select: none;

        &:hover {
            box-shadow: 0px 0px 8px rgba(50, 50, 50, 0.3);
        }
    }

    .type-a {
        border-radius: 50%;
    }

    .type-b {
        border-radius: 50%;
    }

    .type-c {
        height: 30px;
        line-height: 30px;
        border: 1px solid #999;
    }
</style>
