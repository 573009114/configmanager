# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from account.models import BkUser as User
 

class AccountQueryget:
    def __init__(self,**kwargs):
        self.role_group=kwargs.get('role-group')
        self.role_user=kwargs.get('role-user')

    def select_role_user(self):
        """
        查找所有用户组和用户
        """
        result=User.objects.all().values('id','username','groups__name','groups__id')
        return result
    def select_user(self):
        """
        查找所有用户
        """
        result=User.objects.all().values('id','username')
        return result
    def select_permission(self):
        """ 
        根据content_type = 应用名 查所具备的权限
        """
        content_type_id=ContentType.objects.filter(app_label='home_application').values('id')
        result=Permission.objects.filter(content_type_id=content_type_id).values('id','name','codename','content_type_id__model')
        return result
    def select_permission_id(self):
        """
        根据组名，查找权限信息
        """
        result=Permission.objects.filter(name=self.role_group).values('id','name','codename')
        return result
         
    def select_exist_permission(self):
        """
        获取组下的所有权限
        """
        group = Group.objects.get(name=self.role_group)
        result=group.permissions.all()
        return result

    def select_group_id(self):
        """
        根据组名查找组id
        """
        result=Group.objects.filter(name=self.role_group).values('id')
        return result

class AccountQueryset:
    def __init__(self,**kwargs):
        self.role_group=kwargs.get('role-group')
        self.role_user_id=kwargs.get('role-userId')
        self.gid = kwargs.get('gid')
        self.pid = kwargs.get('pid')

    def create_user_group(self):
        """
        创建用户组，并关联组和用户id
        """
        if self.role_group:
            group=Group.objects.create(name=self.role_group)
            group.save()
            gid=group.id
       
        for uid in self.role_user_id[0].split(','):  
            obj=User.objects.filter(id=uid).first()
            obj.groups.add(gid)
        return bool(True)

    def create_group_permission(self):
        """
        清除用户组权限，并赋予新的权限
        """
        obj=Group.objects.filter(id=self.gid).first()
        obj.permissions.clear()
        for pid in self.pid: 
            obj.permissions.add(pid)
        return bool(True)

class AccountQuerydel:
    def __init__(self,**kwargs):
        self.role_group=kwargs.get('role-group')
    def delete_group(self):
        """
        删除用户组
        """
        result=Group.objects.filter(name=self.role_group).delete()
        return result
        



