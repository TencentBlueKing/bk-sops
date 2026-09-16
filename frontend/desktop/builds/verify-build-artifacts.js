/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/

/**
 * 构建产物校验：拦截 render 函数丢失的组件。
 *
 * vue-loader 通过 componentNormalizer(scriptExports, render, staticRenderFns, functionalTemplate, ...)
 * 注册每个 .vue 组件。构建链路（webpack 模块合并 + terser）曾出现过把 render 实参替换成空函数的情况：
 * 模板正确编译出的 render 留在模块作用域里成为死代码，注册时传入的却是 function(){}。
 * 这类组件 render 返回 undefined，Vue 会静默替换成空注释节点——页面整块空白、无 JS 报错、不发任何请求，
 * 只能靠人工点页面才能发现，因此必须在构建阶段卡住。
 *
 * 已知触发条件：terser 5.51.1 会让 TemplateList/index.vue 出现该问题，5.47.1 正常。
 * terser 由 terser-webpack-plugin 以范围依赖引入，因此 package.json 把它锁成精确版本。
 *
 * 用法：
 *   node builds/verify-build-artifacts.js [产物目录]
 * 目录默认为 builds/../static，也可指向解包后的发布包目录，用于校验已产出的 tar 包。
 */
const fs = require('fs')
const path = require('path')

// render 实参为空函数的组件注册调用。第三个实参 [] 与第四个布尔实参共同构成
// componentNormalizer 的签名特征，用于避免误伤普通函数调用。
const EMPTY_RENDER_CALL = /(?:\(\s*0\s*,\s*[\w$]+(?:\.[\w$]+)+\s*\)|[\w$]+(?:\.[\w$]+)*)\(\s*[\w$]+\s*,\s*(?:function\s*\(\s*\)\s*\{\s*\}|\(\s*\)\s*=>\s*\{\s*\})\s*,\s*\[\s*\]\s*,\s*(?:!1|!0|false|true)\s*,/g

// 组件注册调用的尾部特征：staticRenderFns、functionalTemplate、injectStyles、scopeId、moduleIdentifier。
// 不依赖 render 实参内容，因此可用来判断本脚本的匹配规则是否仍然适用于当前构建产物。
const NORMALIZER_CALL_TAIL = /,\s*(?:\[\s*\]|[\w$]+)\s*,\s*(?:!1|!0|false|true)\s*,\s*(?:null|[\w$]+)\s*,\s*(?:"[0-9a-f]{6,}"|null)\s*,\s*(?:null|"[^"]*")\s*\)/g

// webpack moduleIds: 'named' 会把模块路径保留在产物里，用于把问题定位到具体组件。
const MODULE_HEADER = /"(\.\/(?:src|node_modules)\/[^"]+)"\s*\(/g

function collectJsFiles (dir) {
    const files = []
    const walk = (current) => {
        for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
            const full = path.join(current, entry.name)
            if (entry.isDirectory()) {
                walk(full)
            } else if (entry.name.endsWith('.js')) {
                files.push(full)
            }
        }
    }
    walk(dir)
    return files
}

function findEnclosingModule (moduleOffsets, offset) {
    let low = 0
    let high = moduleOffsets.length - 1
    let found = null
    while (low <= high) {
        const mid = (low + high) >> 1
        if (moduleOffsets[mid].offset <= offset) {
            found = moduleOffsets[mid].name
            low = mid + 1
        } else {
            high = mid - 1
        }
    }
    return found
}

function inspectFile (file) {
    const source = fs.readFileSync(file, 'utf8')

    NORMALIZER_CALL_TAIL.lastIndex = 0
    let normalizerCalls = 0
    while (NORMALIZER_CALL_TAIL.exec(source) !== null) {
        normalizerCalls += 1
    }

    const moduleOffsets = []
    MODULE_HEADER.lastIndex = 0
    let moduleMatch
    while ((moduleMatch = MODULE_HEADER.exec(source)) !== null) {
        moduleOffsets.push({ offset: moduleMatch.index, name: moduleMatch[1] })
    }

    const offenders = []
    EMPTY_RENDER_CALL.lastIndex = 0
    let emptyMatch
    while ((emptyMatch = EMPTY_RENDER_CALL.exec(source)) !== null) {
        offenders.push({
            module: findEnclosingModule(moduleOffsets, emptyMatch.index) || '(未能定位所属模块)',
            offset: emptyMatch.index
        })
    }

    return { normalizerCalls, offenders }
}

function main () {
    const target = path.resolve(process.argv[2] || path.join(__dirname, '..', 'static'))

    if (!fs.existsSync(target)) {
        console.error(`[verify-build-artifacts] 产物目录不存在: ${target}`)
        process.exit(1)
    }

    const files = collectJsFiles(target)
    if (files.length === 0) {
        console.error(`[verify-build-artifacts] 目录下没有 .js 产物，请确认已执行构建: ${target}`)
        process.exit(1)
    }

    let normalizerCalls = 0
    const offendersByFile = new Map()

    for (const file of files) {
        const result = inspectFile(file)
        normalizerCalls += result.normalizerCalls
        if (result.offenders.length > 0) {
            offendersByFile.set(file, result.offenders)
        }
    }

    console.log(`[verify-build-artifacts] 扫描 ${files.length} 个 js 产物，识别到 ${normalizerCalls} 处组件注册调用`)

    if (normalizerCalls === 0) {
        console.error('[verify-build-artifacts] 未识别到任何组件注册调用。')
        console.error('  构建链路的产物形态可能已变化，本脚本的匹配规则需要同步更新，否则将失去防护作用。')
        process.exit(1)
    }

    if (offendersByFile.size === 0) {
        console.log('[verify-build-artifacts] 校验通过：没有 render 为空的组件')
        return
    }

    let total = 0
    console.error('\n[verify-build-artifacts] 校验失败：以下组件的 render 在构建产物中为空函数，运行时会渲染为空白且不报错\n')
    for (const [file, offenders] of offendersByFile) {
        total += offenders.length
        console.error(`  ${path.relative(target, file)}  (${offenders.length} 处)`)
        for (const item of new Set(offenders.map(o => o.module))) {
            console.error(`      ${item}`)
        }
    }
    console.error(`\n  共 ${total} 处。首先确认 terser 的实际安装版本：`)
    console.error('      node -p "require(\'terser/package.json\').version"   # 期望与 package.json 中锁定的版本一致')
    console.error('  若不一致，说明依赖解析没有按 package.json 生效（例如构建机 npm 版本过低、读不懂 lockfileVersion 3），')
    console.error('  需清理 node_modules 与 npm 缓存后重装；能用 npm ci 的环境优先用 npm ci。')
    console.error('  若版本一致仍复现，再对比 webpack / terser-webpack-plugin / vue-loader 的实际安装版本。\n')
    process.exit(1)
}

main()
