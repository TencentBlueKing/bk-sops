/**
 * 插件表单脚本（renderform / 内置插件嵌入式表单）统一执行入口
 *
 * 插件表单协议约定：后台返回一段 JS 字符串，脚本通过全局 $ 将表单配置注册到 $.atoms[code]。
 * 为兼容存量插件，此处仍需执行脚本，但做了以下收敛：
 * 1. 全项目只保留这一个执行入口，便于审计与后续接入白名单/沙箱；
 * 2. 使用 new Function 执行，脚本无法通过闭包读取调用方的局部变量（resp 等）；顶层 this 与原 eval 保持一致（调用方组件实例），
 *    配置中的函数（如 remote_data_init、events.action）由 tag 组件以 call(this) 调用，this 仍为 tag 实例，兼容存量插件；
 * 3. 显式只注入全局 $，并以严格类型校验入参，拒绝非字符串内容；
 * 4. 执行异常被隔离，不影响页面其他逻辑，并记录插件标识便于追溯。
 */
export function executePluginFormScript (script, pluginCode = '', context) {
    if (typeof script !== 'string' || !script.trim()) {
        return false
    }
    try {
        // eslint-disable-next-line no-new-func
        const runner = new Function('$', script)
        runner.call(context, window.$)
        return true
    } catch (error) {
        console.error(`[plugin form] execute script failed, plugin: ${pluginCode}`, error)
        return false
    }
}
