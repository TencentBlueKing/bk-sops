<template>
    <div class="global-variable">
        <ul>
            <li
                class="variable-item"
                v-for="(variable, index) in globalVariablesList"
                :key="index">
                <p class="variable-label">{{ variable.label }}</p>
                <p class="variable-value">{{ variable.value }}</p>
            </li>
        </ul>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    export default {
        props: {
            taskId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                globalVariablesList: [
                    {
                        label: '任务的执行者1（${_system.task_name}）',
                        value: 'function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button" class="SideB...”'
                    }, {
                        label: '任务的执行者2（${_system.task_name}）',
                        value: 'function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button" class="SideB...”lue = "确定"; } <input type="button" class="SideB...”function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button"class="SideB...”lue = "确定"; } <input type="button" class="SideB...”class="SideB...”lue = "确定"; } <input'
                    }, {
                        label: '任务的执行者3（${_system.task_name}）',
                        value: 'function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button" class="SideB...”lue = "确定"; } <input type="button" class="SideB...”function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button"class="SideB...”lue = "确定"; } <input type="button" class="SideB...”class="SideB...”lue = "确定"; } <input type="button" class="Sifunction func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button" class="SideB...”lue = "确定";'
                    }, {
                        label: '任务的执行者4（${_system.task_name}）',
                        value: 'function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button" class="SideB...”lue = "确定"; } t<input type="button" class="SideB...”function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="'
                    }, {
                        label: '任务的执行者5（${_system.task_name}）',
                        value: 'function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button" class="SideB...”lue = "确定"; } t<input type="button" class="SideB...”function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="function func(){ var s = document.getElementById("s"); s.value = "确定"; } <input type="button" class="SideB...”'
                    }
                ]
            }
        },
        mounted () {
            this.getGlobalVariablesList()
        },
        methods: {
            ...mapActions('task/', [
                'getRenderCurConstants'
            ]),
            // 获取所有全局变量当前渲染的值
            async getGlobalVariablesList () {
                try {
                    const resp = await this.getRenderCurConstants({ task_id: this.taskId })
                    console.log(resp, '22222')
                } catch (error) {
                    console.warn(error)
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .global-variable {
        padding: 24px;
        .variable-item {
            margin-bottom: 16px;
            font-size: 12px;
            .variable-label {
                color: #63656e;
                margin-bottom: 8px;
            }
            .variable-value {
                min-height: 41px;
                width: 100%;
                background: #fafbfd;
                border: 1px solid #dcdee5;
                border-radius: 3px;
                padding: 12px 16px;
                line-height: 17px;
                color: #c4c6cc;
                word-break: break-all;
                cursor: not-allowed;
            }
        }
    }
</style>
