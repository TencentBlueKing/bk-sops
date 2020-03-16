
function loadRenderFormStyle (url) {
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.type = 'text/css'
    link.href = url
    const head = document.getElementsByTagName('head')[0]
    head.appendChild(link)
}
function loadRenderFormScript (url) {
    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = url
    document.body.appendChild(script)
}

loadRenderFormStyle('/js/renderform/dist/css/index.css')
loadRenderFormScript('/js/renderform/lib/vue.min.js')
loadRenderFormScript('/js/renderform/index.js')