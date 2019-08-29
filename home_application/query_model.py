# -*- coding: utf-8 -*-
from home_application.models import *

class QuerySet:
    """
    写入类
    """
    def __init__(self,**kwargs):
        self.ip=kwargs.get('ip')
        self.server_room=kwargs.get('serverRoom')
        self.service_type=kwargs.get('serviceType')
        self.serverip=kwargs.get('serverip')
        self.group_name=kwargs.get('groupName')
        self.group_id=kwargs.get('groupId')
        self.project_name=kwargs.get('projectName')
        self.sid=kwargs.get('sid')
        self.group_token=kwargs.get('groupToken')
        self.domain=kwargs.get('domain')


    def creat_group(self):    
        """
        创建组
        """
        result=Groups.objects.create(name=self.group_name,typed=self.service_type,
                                        token=self.group_token,nginx_conf='')
        result.save()
        return result.id 

    def creat_ipaddr(self): 
        """
        IP和组进行关联创建
        """
        list=[]
        for i in self.serverip.split(','):
            if i not in list:
                list.append(i)        
        for ip in list:
            getExist=IpAddr.objects.filter(ip=ip).values('id')
            if getExist:
                IpAddr.objects.filter(ip=ip).delete()
            result=IpAddr.objects.create(ip=ip,gid_id=self.sid)
            result.save()            
        return result.id 

    def creat_project(self):
        result=Project.objects.create(name=self.project_name,domain=self.domain,
                                            gid_id=self.group_id,
                                            vhost_conf='',rewrite_conf='')
        result.save()
        return result.id

class QueryUpdate:
    """
    更新数据
    """
    def __init__(self,**kwargs):
        self.id=kwargs.get('id')
        self.vhost=kwargs.get('vhost')
        self.rewrite=kwargs.get('rewrite')
        self.ngx=kwargs.get('nginx')
        self.groupname=kwargs.get('group_name')
        self.gid=kwargs.get('gid')
        self.pid=kwargs.get('pid')

    def update_project(self):
        """
        更新虚拟主机配置和跳转规则配置
        """
        result=Project.objects.filter(id=self.id).update(vhost_conf=self.vhost,rewrite_conf=self.rewrite)
        return result

    def update_group(self):
        """
        更新nginx主配置
        """ 
        result=Groups.objects.filter(id=self.id).update(name=self.groupname,nginx_conf=self.ngx)
        return result

    def update_project_group_bond(self):
        """
        更新域名和项目绑定
        """
        result=Project.objects.filter(id=self.pid).update(gid_id=self.gid)
        return result



class QueryGet:
    """
    查询类
    """ 
    def select_group_all(self):
        """
        查询组信息
        """
        result=Groups.objects.all().values('id','name','typed','token')
        return result 
    def select_project_all_list(self,gid):
        """
        查询所有项目列表
        """
        result=Project.objects.filter(gid_id=gid).values('id','name','vhost_conf','rewrite_conf',
                                             'gid_id__name','gid_id__typed','gid_id__token',
                                             'gid_id__nginx_conf','domain')
        return result

    def select_project_all(self):
        result=Project.objects.all().values('id','domain')
        return result

    def select_project_conf(self,id):
        """
        查询项目配置
        """
        result=Project.objects.filter(id=id).values('vhost_conf','rewrite_conf','gid_id__token','domain')
        return result

    def select_ipaddr_group(self,gid):
        """
        根据组id查询组信息
        """
        result=IpAddr.objects.filter(gid_id=gid).values('id','ip','gid_id__name','gid_id__nginx_conf','gid_id__token')
        return result
    def select_ipaddr_nginx(self,gid):
        """
        根据IP所属组ID查询nginx主配置
        """
        result=Groups.objects.filter(id=gid).values('nginx_conf','name')
        return result

    def select_group_nginx(self,gid):
        """
        根据组id查找nginx配置和token
        """
        result=Groups.objects.filter(id=gid).values('nginx_conf','token')   
        return result 

    def select_group_domain(self,domain):
        """
        根据域名查找业务组类型
        """
        result=Project.objects.filter(domain=domain).values('gid_id__typed')
        return result 

class QueryDel:
    def __init__(self,**kwargs):
        self.id=kwargs.get('id')
    def delete_project(self):
        """
        删除项目
        """
        result=Project.objects.filter(id=self.id).delete()
        return result

    def delete_ip(self):
        """
        删除ip
        """
        result=IpAddr.objects.filter(id=self.id).delete()
        return result

    def delete_group(self):
        """
        删除项目组
        """
        result=Groups.objects.filter(id=self.id).delete()
        return result