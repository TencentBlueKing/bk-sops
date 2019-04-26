<template>
    <div class="tooltip" style="display: none">
        <div v-if="node.type === 'endpoint'">
            <div class="tooltip-arrow"></div>
            <div class="tooltip-inner">
                <div class="tooltip-btn">执行详情</div>
                <div class="tooltip-btn retry-btn">重试</div>
                <div class="tooltip-btn skip-btn">跳过</div>
            </div>
        </div>
        <div v-if="node.type === 'tasknode'">
            <div class="tooltip-arrow"></div>
            <div class="tooltip-inner">
                <div class="tooltip-btn">执行详情</div>
                <div class="tooltip-btn skip-btn">跳过</div>
            </div>
        </div>
        <div v-if="node.type === 'startpoint'">
            <div class="tooltip-arrow"></div>
            <div class="tooltip-inner">
                <div class="tooltip-btn">查看子流程</div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'Tooltips',
        props: {
            node: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                moveFlag: false
            }
        },
        mounted () {

        },
        methods: {

        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .tooltip{
        position: absolute;
        &-arrow{
             position: absolute;
             margin: 6px 0 0 -3px;
             width: 0;
             height: 0;
             border-style: solid;
             border-color: #333333;
             border-width: 0 6px 6px 6px;
             border-left-color: transparent;
             border-right-color: transparent;
             border-top-color: transparent;
             top: -12px;
             left: 50%;
         }
        .tooltip-inner {
            color: #ffffff;
            border-radius: 10px;
            text-align: center;
            background: #29292a;
            padding: 8px 15px;
            white-space: nowrap;
            display: table;
            .tooltip-btn{
                display: table-cell;
                font-size: $fs-14;
                vertical-align: middle;
                + .tooltip-btn:before{
                    content: "|";
                    display: inline-block;
                    padding: 0 10px;
                    color: rgba(255,255,255,0.6);
                }
            }
        }
    }
</style>
