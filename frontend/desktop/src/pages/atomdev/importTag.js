export default function importTag () {
    const innerComponent = require.context(
        '@/components/common/RenderForm/tags/',
        false,
        /Tag[A-Z]\w+\.(vue|js)$/
    )
    // const userComponent = require.context(
    //     '@/components/tags/',
    //     false,
    //     /Tag[A-Z]\w+\.(vue|js)$/
    // )
    const tagComponent = {}
    const tagAttrs = {}
    const register = (fileName, context) => {
        const componentConfig = context(fileName)
        const comp = componentConfig.default
        const attrs = componentConfig.attrs || {}
        const name = fileName.slice(2).slice(0, -4)

        tagComponent[name] = comp
        tagAttrs[name] = attrs
    }
    innerComponent.keys().forEach(fileName => {
        register(fileName, innerComponent)
    })
    // userComponent.keys().forEach(fileName => {
    //     register(fileName, userComponent)
    // })
    return {
        components: tagComponent,
        attrs: tagAttrs
    }
}
