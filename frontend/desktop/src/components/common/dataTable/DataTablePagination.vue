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
<!--封装的分页 table-->
<template>
    <div class="table" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <el-table
            id="DataTablePagination"
            ref="mutipleTable"
            :data="data"
            :stripe="options.stripe"
            :border="options.border"
            :empty-text="i18n.emptyNoData"
            @sort-change="handleSortChange"
            @selection-change="handleSelectionChange">
            <!--选择框-->
            <el-table-column v-if="options.mutiSelect" type="selection" style="width: 55px;">
            </el-table-column>
            <!--选择框end-->
            <!--数据列-->
            <template v-for="(column, index) in columns">
                <el-table-column :key="index" :prop="column.prop" :filters="column.filters" :filter-method="column.handleFilter" :label="column.label" :align="column.align" :width="column.width" :sortable="column.sortable" :min-width="column.minWidth">
                    <template slot-scope="scope">
                        <template v-if="!column.render">
                            <template v-if="column.router">
                                <router-link class="column-name" :to="column.router(scope.row, column)" v-html="column.formatter(scope.row, column)" :title="scope.row.templateName || scope.row.instanceName"></router-link>
                            </template>
                            <template v-else-if="column.formatter">
                                <span v-html="column.formatter(scope.row, column)"></span>
                            </template>
              
                            <template v-else>
                                <span>{{scope.row[column.prop]}}</span>
                            </template>
                        </template>
                        <template v-else>
                            <expand-dom :column="column" :row="scope.row" :render="column.render" :index="index"></expand-dom>
                        </template>
                    </template>
                </el-table-column>
            </template>
            <!--数据列end-->

            <!--按钮操作组-->
            <el-table-column ref="fixedColumn" :label="i18n.operate" align="center" :width="operates.width" :fixed="operates.fixed"
                v-if="operates.isShow && operates.data.filter(_x => _x.show === true).length > 0">
                <template slot-scope="scope">
                    <div class="operate-group">
                        <template v-for="(btn, key) in operates.data">
                            <div class="item" :style="{ flex: operates.flex }" :key="key" v-if="btn.show">
                                <el-button :class="btn.cls" :type="btn.type" size="mini" :icon="btn.icon" :disabled="btn.disabled"
                                    :plain="btn.plain" @click.native.prevent="btn.method(key,scope.row)">{{ btn.label }}
                                </el-button>
                            </div>
                        </template>
                    </div>
                </template>
            </el-table-column>
            <!--按钮操作组end-->
        </el-table>
        <!--分页-->
        <!-- <el-pagination v-if="pagination" @size-change="handleSizeChange"
            @current-change="handleIndexChange"
            :page-size="tableCurrentPagination.limit"
            :page-sizes="tableCurrentPagination.pageArray" :current-page="tableCurrentPagination.pageIndex"
            layout="total,sizes, prev, pager, next, jumper"
            :total="total"
            :pagination="pagination"></el-pagination> -->
        <div class="panagation" v-if="pagination">
            <bk-pagination
                v-if="pagination"
                class=""
                :current="tableCurrentPagination.pageIndex"
                :limit="tableCurrentPagination.limit"
                :limit-list="tableCurrentPagination.pageArray"
                :count="total"
                @change="handleIndexChange"
                @limit-change="handleSizeChange">
            </bk-pagination>
        </div>
    <!--分页end-->
    </div>
</template>
<!--封装的分页 table end-->
<script>
    import '@/utils/i18n.js'
    // 每页展示条数的控制集合
    const _pageArray = [15, 25]

    export default {
        name: 'DataTablePagination',
        components: {
            expandDom: {
                functional: true,
                props: {
                    row: Object,
                    render: Function,
                    index: Number,
                    column: {
                        type: Object,
                        default: null
                    }
                },
                render: (h, ctx) => {
                    const params = {
                        row: ctx.props.row,
                        index: ctx.props.index
                    }
                    if (ctx.props.column) params.column = ctx.props.column
                    return ctx.props.render(h, params)
                }
            }
        },
        props: {
            data: {
                // 需要显示的数据列表
                // prop:表头绑定的字段，
                // label：表头名称，
                // align：每列数据展示形式（left, center, right)，
                // width:列宽
                type: Array,
                default () {
                    return []
                }
            },
            columns: {
                // 需要展示的列
                // prop：列数据对应的属性，
                // label：列名，
                // align：对齐方式，
                // width：列宽，默认为自适应
                // sortable：是否启用排序功能，默认为false
                // formatter: (row, column, cellValue) => {return;}格式化函数
                // render: (h, params) => {return h('el-tag'),{
                //      props: {}
                // }, '显示文字'} //el-tag是标签，如h1,p标签等  显示文字可以通过对应函数再获取
                type: Array,
                default () {
                    return []
                }
            },
            operates: {
                // 后置操作按钮内容
                // isShow: 是否显示后置操作按钮
                // width: 按钮列宽，
                // fixed：是否固定（left,right）
                // list：按钮集合
                //      label: 按钮文本，
                //      type :按钮类型（primary / success / warning / danger / info / text），
                //      show：按钮是否显示，
                //      icon：按钮图标，
                //      plain：按钮是否为朴素按钮，
                //      disabled：按钮是否禁用，
                //      method：按钮回调方法
                type: Object,
                default () {
                    return {}
                }
            },
            total: {
                // 数据总数
                type: Number,
                default: 0
            },
            pagination: {
                // 分页参数
                // limit:每页展示的条数，默认为_page_array[0]，
                // pageIndex:当前页，默认为1，
                // pageArray: 每页展示条数的控制集合，默认 _page_array 即[15, 25]
                type: Object,
                default: () => ({})
            },
            options: {
                // 表格的控制参数
                // stripe 是否为斑马纹 table
                // loading 是否添加表格loading加载动画
                // highlightCurrentRow 是否支持当前行高亮显示
                // mutiSelect 是否支持列表项选中功能
                // filter 是否支持数据过滤功能
                // action 是否支持 表格操作功能
                // border 是否有表格外边框
                type: Object,
                default () {
                    return {
                        stripe: false,
                        loading: false,
                        mutiSelect: false,
                        highlightCurrentRow: false,
                        filter: false,
                        action: false,
                        border: true
                    }
                }
            },
            loading: {
                type: Boolean,
                default () {
                    return false
                }
            }
        },
        data () {
            return {
                i18n: {
                    operate: gettext('操作'),
                    emptyNoData: gettext('无数据')
                },
                // 当前页
                pageIndex: 1,
                // 表格当前分页
                tableCurrentPagination: {
                },

                // 多行选中
                multipleSelection: []
            }
        },
        computed: {
            // 计算table高度
            height () {
                return 1280 - this.otherHeight
            // return this.$utils.Common.getWidthHeight() - this.otherHeight
            }
        },
        created () {
            const { pageIndex, limit, pageArray } = this.pagination
            this.tableCurrentPagination = {
                pageIndex: pageIndex || 1,
                limit: limit || 15,
                pageArray: pageArray || [15, 25]
            }
        },
        methods: {
            // 切换每页显示的数量 size
            handleSizeChange (size) {
                if (this.pagination) {
                    this.tableCurrentPagination = {
                        // 切换每页显示条数后，切换至第一页
                        pageIndex: 1,
                        limit: size,
                        pageArray: _pageArray
                    }
                    this.$emit('handleSizeChange', this.tableCurrentPagination.limit)
                }
            },
            // 切换页码
            handleIndexChange (index) {
                console.log('qihuan')
                if (this.pagination) {
                    // 设置当前页
                    this.tableCurrentPagination.pageIndex = index
                    this.$emit('handleIndexChange', this.tableCurrentPagination.pageIndex)
                }
            },
            // 多行选中
            handleSelectionChange (val) {
                // 将选择的 val 加入至 multipleSelection 中
                this.multipleSelection = val
                this.$emit('handleSelectionChange', val)
            },
            handleSortChange (column, prop, order) {
                this.$emit('handleSortChange', [column, prop, order])
            },
            // 显示 筛选弹窗
            handleFilter () {
                this.$emit('handleFilter')
            },
            // 显示 表格操作弹窗
            handleAction () {
                this.$emit('handleAction')
            }
        }
    }
</script>

<style lang="scss">
.table {
    .el-pagination {
      float: right;
      margin: 20px;
    }
    .el-table__header-wrapper, .el-table__fixed-header-wrapper {
      thead {
        tr {
          th {
            color: #333333;
          }
        }
      }
    }
    .el-table__row{
      td {
        color: #63656e;
      }
    }
    .el-table-column--selection .cell {
      padding: 0;
      text-align: center;
    }
    .el-table__fixed-right {
      bottom: 0 !important;
      right: 6px !important;
      z-index: 1004;
    }
    .operate-group {
      display: flex;
      flex-wrap: wrap;
      .item {
        display: block;
        flex: 0 0 23%;
      }
    }
    .filter-data {
      top: e("calc((100% - 100px) / 3)");
      background-color: rgba(0, 0, 0, 0.7);
    }
    .table-action {
      top: e("calc((100% - 100px) / 2)");
      background-color: rgba(0, 0, 0, 0.7);
    }
    .fix-right {
      position: absolute;
      right: 0;
      height: 100px;
      color: #ffffff;
      width: 30px;
      display: block;
      z-index: 1005;
      writing-mode: vertical-rl;
      text-align: center;
      border-bottom-left-radius: 6px;
      border-top-left-radius: 6px;
      cursor: pointer;
    }
    .btn-size-mini {
        height: 24px;
        line-height: 22px;
        padding: 0 11px;
        font-size: 12px;
    }
}
.column-name {
    color: #3a84ff !important;
}
.el-pagination button, .el-pagination span:not([class*=suffix]) {
    vertical-align: unset;
}
.el-pager, .el-pager li{
    vertical-align: unset;
}
.panagation {
    padding: 10px 20px;
    text-align: right;
    border: 1px solid #dde4eb;
    border-top: none;
    background: #ffff;
}
</style>
