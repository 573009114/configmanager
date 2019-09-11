# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from django.conf.urls import patterns,url 

urlpatterns = patterns(
    '',
    url(r'^$', 'home_application.views.home', name='home'),
    url(r'^project-list/$', 'home_application.views.project_list'),
    url(r'^project-list/edit$', 'home_application.views.project_edit'),
    url(r'^project-list/del$', 'home_application.views.project_delete'),
)

urlpatterns += patterns(
    '',
    (r'^group-list/$', 'home_application.views.group_list'),
    (r'^group-list/edit$', 'home_application.views.group_edit'),
    (r'^group-list/del$', 'home_application.views.group_delete'),
    (r'^group-list/ip/delete$', 'home_application.views.group_list_ipdel'),
)

urlpatterns += patterns(
    '',
    url(r'^cache/other$', 'home_application.views.clear_cache'),
    url(r'^user/authorize$', 'home_application.views.user_authorize'),
    url(r'^user/authorize/edit$', 'home_application.views.user_authorize_edit'),
)

urlpatterns += patterns(
    '',
    (r'^api/v1/group/$', 'home_application.api.group_api'),
    (r'^api/v1/group/push$', 'home_application.api.group_push_api'), 
    (r'^api/v1/ip/$', 'home_application.api.ip_api'), 
    (r'^api/v1/project/$', 'home_application.api.project_api'),
    (r'^api/v1/project/bond$', 'home_application.api.project_bond_api'),
    (r'^api/v1/project/push$', 'home_application.api.project_push_api'), 
    (r'^api/v1/cache/qiniu$', 'home_application.api.qiniu_cache_api'), 
    (r'^api/v1/cache/yun$', 'home_application.api.yuncdn_cache_api'), 
    (r'^api/v1/user/group/$', 'home_application.api.role_group_api'),
    (r'^api/v1/user/group/del$', 'home_application.api.role_group_del_api'),
    (r'^api/v1/user/group/edit$', 'home_application.api.role_group_save_api'), 
    (r'^api/v1/user/group/permission$', 'home_application.api.role_group_permission_api'),
)