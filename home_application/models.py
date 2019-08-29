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
from __future__ import unicode_literals
from django.db import models

class Groups(models.Model):   
    name=models.CharField(max_length=16,unique=True) 
    typed=models.CharField(max_length=32)
    token=models.CharField(max_length=16,unique=True)
    nginx_conf=models.TextField()  
    class Meta():
        default_permissions=[]
        permissions = (
            ("can_add_groups", "添加业务组"),
            ("can_view_groups", "查看业务组"),
            ("can_del_groups", "删除业务组"),
        )    

class IpAddr(models.Model):
    ip=models.GenericIPAddressField(blank=True,null=True,unique=True)
    gid=models.ForeignKey(Groups)
    class Meta():
        default_permissions=[]
        permissions = (
            ("can_add_ipaddr", "添加IP"), 
            ("can_del_ipaddr", "取消关联IP"),
        )
 
        
# class CatalogNgx(models.Model):
#     history=models.CharField(max_length=32,unique=True)   
#     nginx_conf=models.TextField()
#     gid=models.ForeignKey(Groups)
#     class Meta():
#         permissions = (
#             ("can_add_ngx", "添加IP"), 
#             ("can_del_ngx", "取消关联IP"),
#         )  
 

class Project(models.Model):
    name=models.CharField(max_length=32)
    domain=models.CharField(max_length=32)
    vhost_conf=models.TextField()
    rewrite_conf=models.TextField()
    gid=models.ForeignKey(Groups)
    class Meta():
        default_permissions=[]
        permissions = (
            ("can_add_project", "添加项目配置"), 
            ("can_view_project", "查看项目配置"),
            ("can_del_project", "删除项目配置"),
        )    

# class CatalogVhost(models.Model):
#     history=models.CharField(max_length=32,unique=True)
#     vhost_conf=models.TextField()
#     rewrite_conf=models.TextField()
#     pid=models.ForeignKey(Project)
#     class Meta():
#         db_table='confd_catalog_vhost'  
 

# class Search(models.Model):
#     pid=models.ForeignKey(Project)
#     class Meta():
#         permissions = (
#             ("can_view_search", "搜索功能"),
#         )
 