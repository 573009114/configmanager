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
import json
import uuid

from django.http import HttpResponse
from django.shortcuts import render,render_to_response
from django.contrib.auth.decorators import permission_required 

from common.mymako import render_mako_context
from account.decorators import login_exempt

from home_application.models import *
from home_application.query_model import *
from home_application.lib.tencent_api import *
from home_application.lib.etcd_conf import *
from home_application.account_model import *
 
 

def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.htm')


 
def project_list(request):
    """
    项目列表
    """
    
    if not request.user.has_perm('home_application.can_view_project'): 
        return render(request, '403.html')

    try: 
        group=QueryGet().select_group_all()
        _gid=request.GET.get('gid') 
        projects=QueryGet().select_project_all_list(_gid) 
        project_all=QueryGet().select_project_all()
        msg={
            'data': group,
            'project':projects,
            'bondproject':project_all
        }
    except Exception:
        msg={'resultCode':u'50002','data':'','info':u'数据获取错误'} 
    return render_mako_context(request, '/home_application/project-list.htm',{'msg':msg})

def project_edit(request):
    """
    项目编辑
    """
    if not request.user.has_perm('home_application.can_add_project'):
        return render(request, '403.html')

    if request.method == 'POST':  
        pid=request.POST.get('id')      
        vhost=request.POST.get('vhost')
        rewrite=request.POST.get('rewrite')
        
        kwargs={
            'id':pid,
            'vhost':vhost,
            'rewrite':rewrite,
        }
        try: 
            _update_project=QueryUpdate(**kwargs).update_project()
            msg={'resultCode':u'200','data':_update_project,'info': u'更新成功'}
        except Exception:
            msg={'resultCode':'60001','data':'','info': u'创建出错'} 
        return HttpResponse(json.dumps(msg))
    else:
        pid=request.GET.get('id')
        _projects=QueryGet().select_project_conf(id=pid)
        msg={
            'data':_projects,
        }
        return render_mako_context(request, '/home_application/project-content.htm',{'msg':msg}) 
        
def project_delete(request):
    """
    项目删除
    """
    if not request.user.has_perm('home_application.can_del_project'):
        return render(request, '403.html')


    if request.method == 'GET':
        pid=request.GET.get('id')
        project_info=QueryGet().select_project_conf(id=pid)
        for field in project_info:
            fields1='vhost'
            fields2='rewrite'
            token=field['gid_id__token']
            domain=field['domain'] 
        
        vhostKeys=('/%s/%s/%s' %(token,fields1,domain))
        rewriteKeys=('/%s/%s/%s' %(token,fields2,domain))
      
        try:
            delVhost=etcdClient().delKey(vhostKeys) 
        except Exception:
            msg={'info':'Vhost key不存在'}
        try:
           delRewrite=etcdClient().delKey(rewriteKeys)
        except Exception:
            msg={'info':'Rewrite key不存在'}   
        try:
            kwargs={'id':pid}
            _del_project=QueryDel(**kwargs).delete_project()
            msg={'resultCode':u'200','data':'NULL','info': u'完成'}
        except Exception:
            msg={'resultCode':u'60004','data':'','info': u'删除异常'}
        return HttpResponse(json.dumps(msg))

def group_list(request):
    """
    组列表维护
    """
    if not request.user.has_perm('home_application.can_view_groups'):
        return render(request, '403.html')


    if request.method == 'GET':
        _gid=request.GET.get('gid')
        bk_token = request.COOKIES.get('bk_token', '')
        _ip_Id=request.GET.get(id)
        _group=QueryGet().select_group_all()
        _ipaddr=QueryGet().select_ipaddr_group(gid=_gid)
        _ip_list=Handle_Api().handle_host(bk_token)
        msg={
            'group':_group,
            'ipaddr':_ipaddr,
            'iplist':_ip_list,
        }
        return render_mako_context(request, '/home_application/group-list.htm',{'msg':msg})

def group_edit(request):
    """
    编辑组配置
    """
    if not request.user.has_perm('home_application.can_add_groups'):
        return render(request, '403.html')


    if request.method == 'GET':
        _gid=request.GET.get('gid')
        try:
            _group=QueryGet().select_ipaddr_nginx(gid=_gid) 
        except Exception:
            _group="[{'nginx_conf': u'查询异常'}]"
        msg={
            'data':_group,
        }     
        return render_mako_context(request, '/home_application/group-content.htm',{'msg':msg})
    else:
        _gid=request.POST.get('id')
        _ngx_conf=request.POST.get('nginx')
        _group_name=request.POST.get('group-name')

        kwargs={'id':_gid,'nginx':_ngx_conf,'group_name':_group_name}
        try:
            update_ngx=QueryUpdate(**kwargs).update_group()
            msg={'resultCode':u'200','data':'update_ngx','info': u'更新成功'}
        except Exception:
            msg={'resultCode':'60001','data':'','info': u'编辑出错'} 
        return HttpResponse(json.dumps(msg))

def group_delete(request):
    """
    分组删除
    """
    if not request.user.has_perm('home_application.can_del_groups'):
        return render(request, '403.html')

    if request.method == 'GET':
        _gid=request.GET.get('gid')
        try:
            kwargs={'id':_gid}
            _del_project=QueryDel(**kwargs).delete_group()
            msg={'resultCode':u'200','data':'NULL','info': u'完成'}
        except Exception:
            msg={'resultCode':u'60004','data':'','info': u'删除异常'}
        return HttpResponse(json.dumps(msg))

def group_list_ipdel(request):
    """
    删除组ip关联
    """
    if not request.user.has_perm('home_application.can_del_ipaddr'):
        return render(request, '403.html')

    if request.method == 'GET':
        ipId=request.GET.get('ipid')
        try:
            kwargs={'id':ipId}
            _del_project=QueryDel(**kwargs).delete_ip()
            msg={'resultCode':u'200','data':'NULL','info': u'完成'}
        except Exception:
            msg={'resultCode':u'60004','data':'','info': u'删除异常'}
        return HttpResponse(json.dumps(msg)) 

def clear_cache(request):
    """
    缓存清理服务
    """
    return render_mako_context(request, '/home_application/cache-list.htm')

 

def rsync_switch(request):
    """
    发布开关功能，暂未启用
    """
    return render_mako_context(request, '/home_application/switch.htm')

def user_authorize(request):
    """
    权限控制功能
    """
    if not request.user.has_perm('home_application.add_permission'):
        return render(request, '403.html')
    role=AccountQueryget().select_role_user()
    user=AccountQueryget().select_user()
    permission=AccountQueryget().select_permission()
    if request.method == 'POST':
        group=request.POST.get('role-group')
    else:
        group='None'

    try:
        kwargs={'role-group':group}
        is_exist_permission=AccountQueryget(**kwargs).select_exist_permission()
    except Exception:
        is_exist_permission='None'
    print(is_exist_permission)
    #重组数据结构
    role_dic=dict()
    for d in role:
        if d['groups__name'] not in role_dic:          
            role_dic[d['groups__name']]=d['username']
        else:          
            role_dic[d['groups__name']]+=','
            role_dic[d['groups__name']]+=d['username']
    
    new_role=[]
    for k,v in role_dic.items():
        new_role.append({'groups__name':k,'username':v}) 

   
    permission_list=[]
    for p in permission:
        new_permission=dict()
        new_permission["value"]=p['id']
        new_permission["title"]=p['name']
        permission_list.append(new_permission) 

    msg={'role':new_role,'user':user,'permission':json.dumps(permission_list)}
    return render_mako_context(request, '/home_application/permission.htm',{'msg':msg}) 