<template>
    <div class="palette-panel">
        <slot name="palette">
            <ul class="palette-group">
                <li>
                    <div class="palette-default-item startpoint" data-type="startpoint"></div>
                </li>
                <li>
                    <div class="palette-default-item endpoint" data-type="endpoint"></div>
                </li>
                <li>
                    <div class="palette-default-item tasknode" data-type="tasknode"></div>
                </li>
                <li>
                    <div class="palette-default-item gateway" data-type="gateway"></div>
                </li>
            </ul>
        </slot>
    </div>
</template>
<script>
    export default {
        name: 'PalettePanel',
        props: ['selector'],
        data () {
            return {}
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
    .palette-default-item {
        display: inline-block;
        width: 40px;
        height: 40px;
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
    .startpoint {
        border-radius: 50%;
        border: 4px solid #6a6c8a;
    }
    .endpoint {
        border-radius: 50%;
        background: #6a6c8a;
    }
    .tasknode {
        height: 30px;
        border: 2px solid #33d0c6;
    }
    .gateway {
        width: 30px;
        height: 30px;
        background: #7c68fc;
        transform: rotate(-45deg);
    }
</style>
