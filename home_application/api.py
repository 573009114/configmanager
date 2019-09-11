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
import chardet
import os 

from django.http import HttpResponse
from django.shortcuts import render,render_to_response

from common.mymako import render_mako_context
from account.decorators import login_exempt

from home_application.models import *
from home_application.query_model import *
from home_application.account_model import *
from home_application.lib.tencent_api import *
from home_application.lib.etcd_conf import *
from home_application.lib.cdn import *

def group_api(request): 
    
    """
    状态码说明：
    200:成功
    60001: 数据库操作异常
    60002：etcd推送异常 
    60003: 不支持的请求
    接口返回结果示例：{resultCode:200,data:response,info:u'成功'}
    """ 
    """
    创建组接口
    """  
    if not request.user.has_perm('home_application.can_add_groups'): 
        return render(request, '403.html') 

    if request.method == 'POST':      
        service_type=request.POST.get('service-type','')
        group_name=request.POST.get('group-name','')
        group_token=uuid.uuid4()
        kwargs={
            'serviceType':service_type,
            'groupName':group_name,
            'groupToken':group_token,
        }
        try:
            create_group_id=QuerySet(**kwargs).creat_group()           
            msg={'resultCode':u'200','data':create_group_id,'info': u'成功'} 
        except Exception:
            msg={'resultCode':'60001','data':'','info': u'数据库操作异常'}        
        return HttpResponse(json.dumps(msg))
    
    msg={'resultCode':u'60003','data':u'成功','info':u'不支持的请求'}    
    return HttpResponse(json.dumps(msg))

def ip_api(request):
    """
    IP入库接口
    """
    if not request.user.has_perm('home_application.can_add_ipaddr'): 
        return render(request, '403.html') 

    if request.method == 'POST':
        server_room_id=request.POST.get('service-room-id',u'1')
        serverip=request.POST.get('ipaddr') 
        kwargs={'sid':server_room_id,'serverip':serverip}
        try:
            _ip=QuerySet(**kwargs).creat_ipaddr()
      
            msg={'resultCode':u'200','data': _ip,'info': u'成功'}
        except Exception:
 
            msg={'resultCode':u'60001','data':'','info': u'数据库操作异常，非法的请求'}
        return  HttpResponse(json.dumps(msg))
    else:
        msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'} 
        return  HttpResponse(json.dumps(msg)) 

def project_bond_api(request):
    """
    更新绑定
    """
    if not request.user.has_perm('home_application.can_add_ipaddr'): 
        return render(request, '403.html') 
    if request.method == 'POST':
        pid=request.POST.get('pid')
        gid=request.POST.get('group-id')
        kwargs={'gid':gid,'pid':pid} 
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
            _project=QueryUpdate(**kwargs).update_project_group_bond()
            
            msg={'resultCode':u'200','data': _project,'info': u'成功'}
        except Exception:
            msg={'resultCode':u'60001','data':'','info': u'数据库操作异常，非法的请求'}
        return  HttpResponse(json.dumps(msg))
    msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'} 
    return  HttpResponse(json.dumps(msg))

def project_api(request):
    """
    创建项目接口
    """   
    if not request.user.has_perm('home_application.can_add_project'): 
        return render(request, '403.html') 

    if request.method == 'POST':        
        groupId=request.POST.get('group-id','')
        projectName=request.POST.get('project-name','')
        domain=request.POST.get('domain','')
        domainId=request.POST.get('domain-id',1)

        if domainId == '1':
            main_domain='.a.com.cn'
        elif domainId == '2':
            main_domain='.b.com'
        else:
            main_domain=''
        new_domain=domain+main_domain
        
        kwargs={
            'groupId':groupId,
            'projectName':projectName,
            'domain':new_domain,
        }
        try:
            create_project=QuerySet(**kwargs).creat_project()  
            msg={'resultCode':u'200','data':create_project,'info': u'创建成功'} 
        except Exception:
            msg={'resultCode':'60001','data':'','info': u'数据库操作异常,注意不要重复'}
        return HttpResponse(json.dumps(msg))
    msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
    return HttpResponse(json.dumps(msg)) 

def group_push_api(request):
    """
    推送全局配置接口
    主配置key书写规范：   /$TOKEN/nginx/ 
    客户端查找key值得方法：根据IP找到组ID，然后获取token，之后拼接nginx字段，获取value
    """
    if request.method == 'POST':
        groupId=request.POST.get('gid')
        obtain_ngx_conf=QueryGet().select_ipaddr_group(gid=groupId)
  
        for field in obtain_ngx_conf:            
            token=field['gid_id__token']
            fields='nginx'
            nginx_conf=field['gid_id__nginx_conf']
        try:
            nginxKeys=('/%s/%s' %(token,fields))
            pushEtcd=etcdClient().writeValue(nginxKeys,nginx_conf)
            msg={'resultCode':u'200','data':u'','info':u'推送成功'} 
        except Exception:
            msg={'resultCode':u'60002','data':u'','info':u'etcd推送异常，请检查是否绑定后端'} 
        return HttpResponse(json.dumps(msg))   
    msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'} 
    return HttpResponse(json.dumps(msg))  
 
def project_push_api(request):
    """
    项目信息推送接口
    虚拟主机key书写规范： /$TOKEN/vhost/$项目名/
    跳转规则key书写规范： /$TOKEN/rewrite/$项目名/
    """
    if not request.user.has_perm('home_application.can_add_project'): 
        return render(request, '403.html') 

    if request.method == 'POST':
        pid=request.POST.get('pid')
        project_info=QueryGet().select_project_conf(id=pid)  
        fields1='vhost'
        fields2='rewrite'
        token=project_info[0]['gid_id__token']
        domain=project_info[0]['domain']
        vhost=project_info[0]['vhost_conf'].encode('utf8')
        rewrite=project_info[0]['rewrite_conf'].encode('utf8')

        #解决编码导致的配置文件生成异常
        vhost_open=open('tmp/%s_vhost' %domain,'w')
        vhost_open.write(vhost) 
        vhost_open.close()
        os.system("sed -i 's/\xc2\xa0/ /g' tmp/%s_vhost" %domain) 

        rewrite_open=open('tmp/%s_rewrite' %domain,'w')
        rewrite_open.write(rewrite) 
        rewrite_open.close() 
        os.system("sed -i 's/\xc2\xa0/ /g' tmp/%s_rewrite" %domain)
         
        vhost_txt=open('tmp/%s_vhost'%domain).read()
        rewrite_txt=open('tmp/%s_rewrite'%domain).read()

        if vhost != '':
            if rewrite == '': 
                vhostKeys=('/%s/%s/%s' %(token,fields1,domain)) 
                pushVhost=etcdClient().writeValue(vhostKeys,vhost_txt)
                msg={'resultCode':u'200','data':u'','info':u'推送成功，rewrite内容为空'}
            else:
                vhostKeys=('/%s/%s/%s' %(token,fields1,domain))
                rewriteKeys=('/%s/%s/%s' %(token,fields2,domain))
                pushVhost=etcdClient().writeValue(vhostKeys,vhost_txt)
                pushRewrite=etcdClient().writeValue(rewriteKeys,rewrite_txt)
                msg={'resultCode':u'200','data':u'','info':u'etcd推送成功'} 
            return HttpResponse(json.dumps(msg))
        else:
            msg={'resultCode':u'60002','data':u'','info':u'推送失败，vhost内容为空'}
            return HttpResponse(json.dumps(msg)) 
    msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
    return HttpResponse(json.dumps(msg)) 

def qiniu_cache_api(request):
    """
    清除七牛缓存
    """
    if request.method == 'POST':
        url=request.POST.get('url') 
        try:
            refresh_url_result = clear_qiniu(url) 
            msg={'resultCode':u'200','data':refresh_url_result,'info':refresh_url_result}
        except Exception:
            msg={'resultCode':u'60005','data':refresh_url_result,'info':u'提交失败'}
        return HttpResponse(json.dumps(msg))
    else:
        msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
        return HttpResponse(json.dumps(msg)) 

def yuncdn_cache_api(request):
    """
    清除云端cdn缓存
    """
    if request.method == 'POST':
        url=request.POST.get('url')
        AppID,Sgn,Date,AppSecret=yun_config()
        data={
            'files': [url],
            'appid': AppID,
            'request_time': Date,
            'signature': Sgn
        }

        try:
            refresh_url_result=yun_task(data)
            msg={'resultCode':u'200','data':refresh_url_result,'info':refresh_url_result['result']['task_id']}
        except Exception:
            msg={'resultCode':u'60005','data':refresh_url_result,'info':u'提交失败'}
        return HttpResponse(json.dumps(msg))
    else:
        msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
        return HttpResponse(json.dumps(msg))  

def role_group_api(request):
    """
    角色组接口
    """
    if request.method == 'POST':
        group=request.POST.get('role-group')
        userId=request.POST.getlist('users-id')
        kwargs={
            'role-group':group,
            'role-userId':userId        
        }
        
        try:
            result=AccountQueryset(**kwargs).create_user_group()
            msg={'resultCode':u'200','data':result,'info':u'创建成功'}
        except Exception:
            msg={'resultCode':u'60005','data':'null','info':u'提交失败'} 
        return HttpResponse(json.dumps(msg))  
    else:
        msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
        return HttpResponse(json.dumps(msg)) 
def role_group_del_api(request):
    """
    删除记录
    """
 
    if request.method =='GET':
        group=request.GET.get('rolename').encode('utf-8')
        print(group)
        kwargs={'role-group':group}
        result=AccountQuerydel(**kwargs).delete_group()
        msg={'resultCode':u'200','data':result,'info':u'删除成功'}
        return HttpResponse(json.dumps(msg)) 
    else:
        msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
        return HttpResponse(json.dumps(msg)) 

def role_group_permission_api(request):
    """
    权限管理模块
    """
    if not request.user.has_perm('home_application.add_permission'): 
        return render(request, '403.html') 


    if request.method == 'POST':
        permission=request.POST.getlist('Data')
        group=request.POST.get('role-group')
        
        #根据用户组名查id
        kwargs={'role-group':group}
        try:
            gid=AccountQueryget(**kwargs).select_group_id()
        except:
            gid=''

        pid=[]
        for permission_id in json.loads(permission[0]):
            pid.append(permission_id['value'])
        kwargs['gid']=gid
        kwargs['pid']=pid
        
        try:
            result=AccountQueryset(**kwargs).create_group_permission()
            msg={'resultCode':u'200','data':result,'info':u'成功'}
        except Exception:
            msg={'resultCode':u'60001','data':'','info':u'失败的请求'}
        return HttpResponse(json.dumps(msg)) 

    else:
        msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
        return HttpResponse(json.dumps(msg)) 

def role_group_save_api(request):
    if request.method == 'POST':
        group_name=request.POST.get('group-name').encode('utf-8')
        userId=request.POST.getlist('users-id')
        kwargs={'group-name':group_name,'UID':userId} 
        try:
          
            result=AccountQueryupdate(**kwargs).update_roles()

            msg={'resultCode':u'200','data':result,'info':u'成功'}
        except Exception:
            msg={'resultCode':u'60001','data':'','info':u'失败的请求'}
        return HttpResponse(json.dumps(msg))
    else:
        msg={'resultCode':u'60003','data':u'','info':u'不支持的请求'}    
        return HttpResponse(json.dumps(msg)) 