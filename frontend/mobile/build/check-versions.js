/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import childProcess from 'child_process'

import chalk from 'chalk'
import semver from 'semver'
import shell from 'shelljs'

import pkg from '../package.json'

/**
 * 执行命令
 *
 * @param {string} cmd 命令语句
 *
 * @return {string} 命令执行结果
 */
const exec = cmd => childProcess.execSync(cmd).toString().trim()

const versionRequirements = [
    {
        name: 'node',
        currentVersion: semver.clean(process.version),
        versionRequirement: pkg.engines.node
    }
]

if (shell.which('npm')) {
    versionRequirements.push({
        name: 'npm',
        currentVersion: exec('npm --version'),
        versionRequirement: pkg.engines.npm
    })
}

export default function () {
    const warnings = []
    for (let i = 0; i < versionRequirements.length; i++) {
        const mod = versionRequirements[i]
        if (!semver.satisfies(mod.currentVersion, mod.versionRequirement)) {
            warnings.push(mod.name
                + ': '
                + chalk.red(mod.currentVersion)
                + ' should be '
                + chalk.green(mod.versionRequirement)
            )
        }
    }

    if (warnings.length) {
        console.log('')
        console.log(chalk.yellow('To use this template, you must update following to modules:'))
        console.log()
        for (let i = 0; i < warnings.length; i++) {
            console.log('  ' + warnings[i])
        }
        console.log()
        process.exit(1)
    }
}
