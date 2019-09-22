/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import '@/utils/i18n.js'
import { mapState } from 'vuex'
import tools from '@/utils/tools.js'
export const AnalysisMixins = {
    data () {
        return {
            dataTablePageArray: [15, 25], // 全局的dataTable控制每页数量
            dataTableOptions: {
                stripe: true, // 是否为斑马纹
                loading: false, // 是否添加表格loading加载动画
                highlightCurrentRow: true, // 是否支持当前行高亮显示
                mutiSelect: false, // 是否支持列表项选中功能
                filter: false, // 是否支持数据过滤功能
                action: true, // 是否支持表格操作功能
                border: true // 是否支持外边框
            },
            category: undefined,
            bizCcId: undefined,
            selectedCcId: '',
            choiceCategory: '',
            choiceBusiness: '',
            selectedCategory: '',
            businessSelected: '',
            categorySelected: ''
        }
    },
    computed: {
        ...mapState({
            allBusinessList: state => state.allBusinessList,
            categorys: state => state.categorys
        }),
        businessList () {
            if (this.allBusinessList.length === 0) {
                this.getBizList(1)
            }
            const list = tools.deepClone(this.allBusinessList)
            return list
        },
        categoryList () {
            if (this.categorys.length === 0) {
                this.getCategorys()
            }
            const list = tools.deepClone(this.categorys)
            return list
        }
    },
    mounted () {
        const ulList = document.querySelectorAll('.outside-ul')
        for (const item of ulList) {
            item.style['max-height'] = '250px'
        }
    },
    methods: {
        getUTCTime (time) {
            time = time.slice() // 防止引用 重新创建
            time[0] = new Date(time[0]).setHours(0, 0, 0) // 将创建时间设置为0点0分0秒
            time[1] = new Date(time[1]).setHours(0, 0, 0) // 将创建时间设置为0点0分0秒
            return time
        },
        onSelectedCategory (name, value) {
            if (this.category === name) {
                return
            }
            this.selectedCategory = name
            this.category = name
            this.resetPageIndex()
            this.onChangeTabPanel(this.tabName)
        },
        onSelectedBizCcId (name, value) {
            if (this.bizCcId === name) {
                return
            }
            this.selectedCcId = name
            this.bizCcId = name
            this.resetPageIndex()
            this.onChangeTabPanel(this.tabName)
        },
        onClearBizCcId () {
            this.selectedCcId = ''
            this.bizCcId = undefined
            this.resetPageIndex()
            this.onChangeTabPanel(this.tabName)
        },
        onClearCategory () {
            this.selectedCategory = ''
            this.category = undefined
            this.resetPageIndex()
            this.onChangeTabPanel(this.tabName)
        }
    }
}
