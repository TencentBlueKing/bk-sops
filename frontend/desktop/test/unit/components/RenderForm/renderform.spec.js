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

import { shallowMount, mount } from '@vue/test-utils'
import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
import FormGroup from '@/components/common/RenderForm/FormGroup.vue'
import FormItem from '@/components/common/RenderForm/FormItem.vue'
import TagInput from '@/components/common/RenderForm/tags/TagInput.vue'
import singlePlugin from './singlePlugin.js'
import combinePlugin from './combinePlugin.js'

describe('RenderForm', () => {
  it('should formItem render correct', () => {
    const wrapper = shallowMount(RenderForm, {
      propsData: {
        scheme: singlePlugin
      }
    })
    expect(wrapper.find('.render-form').exists()).toBe(true)

    const formItem = wrapper.find(FormItem)
    expect(formItem.exists()).toBe(true)
    expect(wrapper.props().formData).toHaveProperty('bk_timing')
  })

  it('should combine form render correct', () => {
    const wrapper = shallowMount(RenderForm, {
      propsData: {
        scheme: combinePlugin 
      }
    })
    expect(wrapper.find('.render-form').exists()).toBe(true)

    const formGroup = wrapper.find(FormGroup)
    const formItem = wrapper.find(FormItem)
    expect(formGroup.exists()).toBe(true)
    expect(formItem.exists()).toBe(true)
    expect(wrapper.props().formData).toEqual({
      bk_notify_title: '',
      bk_receiver_info: {
        bk_more_receiver: '',
        bk_receiver_group: ['Maintainers']
      }
    })
  })
})
