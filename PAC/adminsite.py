# 管理员站点 配置系统名字，大标题，logo，版权信息
from django.contrib import admin# 导入admin
from django.contrib.admin.apps import AdminConfig# 导入AdminConfig
from django.utils.html import format_html

class AdminSite(admin.AdminSite):
    site_header = 'PC配件管理系统'# 设置系统名字
    site_title = 'PC配件管理后台'# 设置大标题
    index_title = '系统管理'# 设置首页标题
    site_footer = format_html('&copy; 2024 PC配件管理系统 - All Rights Reserved by 21060423')# 设置版权信息

    # 自定义管理后台的样式
    def each_context(self, request):
        context = super().each_context(request)
        context['custom_css'] = """
            :root {
                --primary: #1a73e8;
                --secondary: #4285f4;
            }
            #header {
                background: var(--primary);
                color: #fff;
            }
            .module h2, .module caption {
                background: var(--primary);
            }
            div.breadcrumbs {
                background: var(--secondary);
            }
            .button, input[type=submit], input[type=button] {
                background: var(--primary);
            }
        """
        return context

class AdminConfig(AdminConfig):
    default_site = "PAC.adminsite.AdminSite"
