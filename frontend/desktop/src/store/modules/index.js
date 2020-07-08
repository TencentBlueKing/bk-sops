/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import template from './template.js'
import templateList from './templateList.js'
import task from './task.js'
import taskList from './taskList.js'
import atomForm from './atomForm.js'
import atomDev from './atomDev.js'
import appmaker from './appmaker'
import project from './project'
import functionTask from './function.js'
import auditTask from './audit.js'
import periodic from './periodic.js'
import manage from './manage.js'
import admin from './admin.js'

const modules = {
    template,
    templateList,
    task,
    taskList,
    atomForm,
    atomDev,
    appmaker,
    functionTask,
    auditTask,
    periodic,
    manage,
    project,
    admin
}

export default modules
