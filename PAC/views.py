from django.shortcuts import render, redirect
from django.http import JsonResponse
import psutil
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CPU, GraphicsCard, Motherboard, Memory, HardDisk, PowerSupply
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from selenium.webdriver.edge.options import Options
import re
from django.utils.safestring import mark_safe
from decimal import Decimal
import requests
import tempfile
import shutil
import os

# Create your views here.
@login_required(login_url='/login/')
def index(request):
    # 获取最新的显卡数据
    latest_gpu = GraphicsCard.objects.filter(price__isnull=False).order_by('-created_at').first()
    latest_cpu = CPU.objects.filter(price__isnull=False).order_by('-created_at').first()
    
    context = {
        'username': request.user.username,
        'latest_gpu': latest_gpu,
        'latest_cpu': latest_cpu
    }
    return render(request, 'index.html', context)

@login_required(login_url='/login/')
def zero(request):
    return render(request, 'zero.html')

@login_required(login_url='/login/')
def autowx(request):
    return render(request, 'autowx.html')

def create_headless_driver():
    """创建Edge浏览器实例（无头模式）"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    driver = None
    
    options = Options()
    # 启用无头模式
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # 使用临时目录作为用户数据目录
    options.add_argument(f'--user-data-dir={temp_dir}')
    # 禁用扩展和自动更新
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-component-update')
    # SSL证书和DNS配置
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--dns-prefetch-disable')
    # 添加新的选项以提高稳定性
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # 设置更保守的页面加载策略
    options.page_load_strategy = 'normal'
    # 设置窗口大小
    options.add_argument('--window-size=1920,1080')
    # 添加用户代理
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
    # 增加超时设置
    options.add_argument('--browser-test-mode')
    options.add_argument('--no-first-run')
    options.add_argument('--disable-hang-monitor')
    options.add_argument('--disable-background-networking')
    
    try:
        driver = webdriver.Edge(options=options)
        driver.maximize_window()
        # 增加超时时间设置
        driver.set_page_load_timeout(60)  # 增加到60秒
        driver.set_script_timeout(60)     # 增加到60秒
        driver.implicitly_wait(20)        # 增加隐式等待时间
        driver._temp_dir = temp_dir
        return driver
    except Exception as e:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"创建浏览器实例失败: {str(e)}")
        raise

def get_brand_from_name(name, brand_keywords):
    """
    从产品名称中识别品牌
    brand_keywords: dict, key为品牌名，value为关键词列表
    """
    name_upper = name.upper()
    for brand, keywords in brand_keywords.items():
        if any(keyword.upper() in name_upper for keyword in keywords):
            return brand
    return "其他"

# 修改 clean_price_for_db 函数
def clean_price_for_db(price_str):
    """清理价格字符串，只保留数字部分，返回Decimal类型或None"""
    if not price_str or price_str in ['暂无价格', '价格待定']:
        return None
    try:
        # 移除所有非数字和小数点的字符
        cleaned = ''.join(c for c in str(price_str) if c.isdigit() or c == '.')
        if not cleaned:
            return None
        # 确保只有一个小数点
        if cleaned.count('.') > 1:
            cleaned = cleaned.replace('.', '', cleaned.count('.') - 1)
        return Decimal(cleaned)
    except:
        return None

@login_required(login_url='/login/')
def cpu_view(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        print("\n开始爬取CPU数据...")
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='cpu_')
        
        # 创建Edge浏览器选项
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        options.add_argument(f'--user-data-dir={temp_dir}')
        
        # 创建Edge浏览器实例
        driver = webdriver.Edge(options=options)
        # 最大化浏览器窗口
        driver.maximize_window()
        
        try:
            print("正在访问中关村在线CPU页面...")
            driver.get("https://detail.zol.com.cn/cpu/")
            time.sleep(3)
            
            print("清空现有CPU数据...")
            CPU.objects.all().delete()
            
            page_num = 1
            max_pages = 20
            total_items = 0
            
            while page_num <= max_pages:
                print(f"\n正在处理第 {page_num} 页...")
                # 等待产品列表加载完成
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-follow-id^='p']"))
                    )
                except Exception as e:
                    print(f"等待产品列表加载失败: {e}")
                    time.sleep(5)
                
                # 滚动页面到底部以加载所有内容
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                products = soup.find_all('li', attrs={'data-follow-id': lambda x: x and x.startswith('p')})
                
                if not products:
                    print("未找到产品信息，可能页面结构有变化")
                    break
                
                print(f"在第 {page_num} 页找到 {len(products)} 个产品")
                
                for i, product in enumerate(products, 1):
                    try:
                        name_elem = product.find('h3').find('a')
                        name = name_elem.get('title', '未知名称')
                        
                        # 获取价格 - 更新价格获取逻辑
                        price_elem = product.find('span', class_='price-normal')
                        if price_elem:
                            price_type = price_elem.find('b', class_='price-type')
                            price = price_type.text if price_type else "暂无价格"
                        else:
                            price = "暂无价格"
                        
                        # 获取评分
                        score_elem = product.find('span', class_='score')
                        score = score_elem.text if score_elem else "暂无评分"
                        
                        # 获取评论数
                        comment_elem = product.find('a', class_='comment-num')
                        comment_count = comment_elem.text if comment_elem else "0人点评"
                        
                        # 清理价格并保存
                        cleaned_price = clean_price_for_db(price)
                        if cleaned_price:
                            CPU.objects.create(
                                name=name,
                                price=cleaned_price,
                                score=score,
                                comments=comment_count
                            )
                            total_items += 1
                            print(f"[{page_num}-{i}] 成功保存: {name} - {price} - 评分:{score} - {comment_count}")
                        else:
                            print(f"[{page_num}-{i}] 跳过无效价格产品: {name}")
                            
                    except Exception as e:
                        print(f"[{page_num}-{i}] 提取产品信息时出错: {e}")
                        continue
                
                if page_num == max_pages:
                    print("\n已达到指定的最大页数限制")
                    break
                
                # 查找并点击下一页按钮
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next"))
                    )
                    if "disabled" in next_button.get_attribute("class"):
                        print("已到达最后一页")
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"翻页失败或已到最后一页: {e}")
                    break
                    
        except Exception as e:
            print(f"\n爬取过程中出现错误: {e}")
            raise Exception(f"爬取CPU数据失败: {str(e)}")
        finally:
            print("\n关闭浏览器...")
            try:
                driver.quit()
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")
            print(f"\nCPU数据爬取完成，共保存 {total_items} 条记录")
            
    # 获取最新爬取的数据，过滤并排序
    cpu_list = CPU.objects.exclude(price__isnull=True).order_by('-price')
    
    # 获取所有品牌的CPU并排序
    brands = {
        'Intel': [],
        'AMD': []
    }
    
    for cpu in cpu_list:
        # 确保价格显示正确
        if cpu.price:
            cpu.price = mark_safe(f"{cpu.price}￥")
            
        if 'Intel' in cpu.name:
            brands['Intel'].append(cpu)
        elif 'AMD' in cpu.name:
            brands['AMD'].append(cpu)
    
    context = {
        'cpu_list': cpu_list,
        'brands': brands
    }
    return render(request, 'CPU.html', context)

# 添加一个辅助函数来处理价格
def process_price(price_str):
    # 移除所有可能的¥符号并清理空格
    price = price_str.replace('¥', '').strip()
    try:
        # 转换为数字并格式化
        price_num = float(price.replace(',', ''))
        return f"{price_num:,.0f}￥"
    except ValueError:
        return price_str

def extract_price_number(price_str):
    """从价格字符串中提取数字"""
    try:
        return float(''.join(filter(str.isdigit, str(price_str))))
    except ValueError:
        return 0

@login_required(login_url='/login/')
def xianka(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        print("\n开始爬取显卡数据...")
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='gpu_')
        
        # 创建Edge浏览器选项
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        options.add_argument(f'--user-data-dir={temp_dir}')
        
        # 创建Edge浏览器实例
        driver = webdriver.Edge(options=options)
        # 最大化浏览器窗口
        driver.maximize_window()
        
        try:
            print("正在访问中关村在线显卡页面...")
            driver.get("https://detail.zol.com.cn/vga/")
            time.sleep(3)
            
            print("清空现有显卡数据...")
            GraphicsCard.objects.all().delete()
            
            page_num = 1
            max_pages = 20
            total_items = 0
            
            while page_num <= max_pages:
                print(f"\n正在处理第 {page_num} 页...")
                # 等待产品列表加载完成
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-follow-id^='p']"))
                    )
                except Exception as e:
                    print(f"等待产品列表加载失败: {e}")
                    time.sleep(5)
                
                # 滚动页面到底部以加载所有内容
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                products = soup.find_all('li', attrs={'data-follow-id': lambda x: x and x.startswith('p')})
                
                if not products:
                    print("未找到产品信息，可能页面结构有变化")
                    break
                
                print(f"在第 {page_num} 页找到 {len(products)} 个产品")
                
                for i, product in enumerate(products, 1):
                    try:
                        name_elem = product.find('h3').find('a')
                        name = name_elem.get('title', '未知名称')
                        
                        # 获取价格 - 更新价格获取逻辑
                        price_elem = product.find('span', class_='price-normal')
                        if price_elem:
                            price_type = price_elem.find('b', class_='price-type')
                            price = price_type.text if price_type else "暂无价格"
                        else:
                            price = "暂无价格"
                        
                        # 获取评分
                        score_elem = product.find('span', class_='score')
                        score = score_elem.text if score_elem else "暂无评分"
                        
                        # 获取评论数
                        comment_elem = product.find('a', class_='comment-num')
                        comment_count = comment_elem.text if comment_elem else "0人点评"
                        
                        # 清理价格并保存
                        cleaned_price = clean_price_for_db(price)
                        if cleaned_price:
                            GraphicsCard.objects.create(
                                name=name,
                                price=cleaned_price,
                                score=score,
                                comments=comment_count
                            )
                            total_items += 1
                            print(f"[{page_num}-{i}] 成功保存: {name} - {price} - 评分:{score} - {comment_count}")
                        else:
                            print(f"[{page_num}-{i}] 跳过无效价格产品: {name}")
                            
                    except Exception as e:
                        print(f"[{page_num}-{i}] 提取产品信息时出错: {e}")
                        continue
                
                if page_num == max_pages:
                    print("\n已达到指定的最大页数限制")
                    break
                
                # 查找并点击下一页按钮
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next"))
                    )
                    if "disabled" in next_button.get_attribute("class"):
                        print("已到达最后一页")
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"翻页失败或已到最后一页: {e}")
                    break
                    
        except Exception as e:
            print(f"\n爬取过程中出现错误: {e}")
            raise Exception(f"爬取显卡数据失败: {str(e)}")
        finally:
            print("\n关闭浏览器...")
            try:
                driver.quit()
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")
            print(f"\n显卡数据爬取完成，共保存 {total_items} 条记录")
            
    graphics_cards = GraphicsCard.objects.exclude(price__isnull=True).order_by('-price')
    page_config = {
        'title': '显卡信息',
        'icon_class': 'fas fa-tv',
        'item_type': '显卡'
    }
    context = {
        'items': graphics_cards,
        'page_config': page_config
    }
    return render(request, 'xianka.html', context)

@login_required(login_url='/login/')
def zhuban(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        print("\n开始爬取主板数据...")
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='motherboard_')
        
        # 创建Edge浏览器选项
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        options.add_argument(f'--user-data-dir={temp_dir}')
        
        # 创建Edge浏览器实例
        driver = webdriver.Edge(options=options)
        # 最大化浏览器窗口
        driver.maximize_window()
        
        try:
            print("正在访问中关村在线主板页面...")
            driver.get("https://detail.zol.com.cn/motherboard/")
            time.sleep(3)
            
            print("清空现有主板数据...")
            Motherboard.objects.all().delete()
            
            page_num = 1
            max_pages = 20
            total_items = 0
            
            while page_num <= max_pages:
                print(f"\n正在处理第 {page_num} 页...")
                # 等待产品列表加载完成
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-follow-id^='p']"))
                    )
                except Exception as e:
                    print(f"等待产品列表加载失败: {e}")
                    time.sleep(5)
                
                # 滚动页面到底部以加载所有内容
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                products = soup.find_all('li', attrs={'data-follow-id': lambda x: x and x.startswith('p')})
                
                if not products:
                    print("未找到产品信息，可能页面结构有变化")
                    break
                
                print(f"在第 {page_num} 页找到 {len(products)} 个产品")
                
                for i, product in enumerate(products, 1):
                    try:
                        name_elem = product.find('h3').find('a')
                        name = name_elem.get('title', '未知名称')
                        
                        # 获取价格 - 更新价格获取逻辑
                        price_elem = product.find('span', class_='price-normal')
                        if price_elem:
                            price_type = price_elem.find('b', class_='price-type')
                            price = price_type.text if price_type else "暂无价格"
                        else:
                            price = "暂无价格"
                        
                        # 获取评分
                        score_elem = product.find('span', class_='score')
                        score = score_elem.text if score_elem else "暂无评分"
                        
                        # 获取评论数
                        comment_elem = product.find('a', class_='comment-num')
                        comment_count = comment_elem.text if comment_elem else "0人点评"
                        
                        # 清理价格并保存
                        cleaned_price = clean_price_for_db(price)
                        if cleaned_price:
                            Motherboard.objects.create(
                                name=name,
                                price=cleaned_price,
                                score=score,
                                comments=comment_count
                            )
                            total_items += 1
                            print(f"[{page_num}-{i}] 成功保存: {name} - {price} - 评分:{score} - {comment_count}")
                        else:
                            print(f"[{page_num}-{i}] 跳过无效价格产品: {name}")
                            
                    except Exception as e:
                        print(f"[{page_num}-{i}] 提取产品信息时出错: {e}")
                        continue
                
                if page_num == max_pages:
                    print("\n已达到指定的最大页数限制")
                    break
                
                # 查找并点击下一页按钮
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next"))
                    )
                    if "disabled" in next_button.get_attribute("class"):
                        print("已到达最后一页")
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"翻页失败或已到最后一页: {e}")
                    break
                    
        except Exception as e:
            print(f"\n爬取过程中出现错误: {e}")
            raise Exception(f"爬取主板数据失败: {str(e)}")
        finally:
            print("\n关闭浏览器...")
            try:
                driver.quit()
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")
            print(f"\n主板数据爬取完成，共保存 {total_items} 条记录")
            
    # 获取主板数据并格式化价格显示
    motherboards = Motherboard.objects.exclude(price__isnull=True).order_by('-price')
    for motherboard in motherboards:
        if motherboard.price:
            motherboard.price = mark_safe(f"{motherboard.price}￥")
            
    page_config = {
        'title': '主板信息',
        'icon_class': 'fas fa-microchip',
        'item_type': '主板'
    }
    context = {
        'motherboards': motherboards,
        'page_config': page_config
    }
    return render(request, 'zhuban.html', context)

@login_required(login_url='/login/')
def neicun(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        return get_memories(request)
    
    memories = Memory.objects.exclude(price__isnull=True).order_by('-price')
    page_config = {
        'title': '内存信息',
        'icon_class': 'fas fa-memory',
        'item_type': '内存'
    }
    context = {
        'items': memories,
        'page_config': page_config
    }
    return render(request, 'neicun.html', context)

@login_required(login_url='/login/')
def yingpan(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        return get_hard_disks(request)
    
    hard_disks = HardDisk.objects.exclude(price__isnull=True).order_by('-price')
    page_config = {
        'title': '硬盘信息',
        'icon_class': 'fas fa-hdd',
        'item_type': '硬盘'
    }
    context = {
        'items': hard_disks,
        'page_config': page_config
    }
    return render(request, 'yingpan.html', context)

@login_required(login_url='/login/')
def dianyuan(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        return get_power_supplies(request)
    
    power_supplies = PowerSupply.objects.exclude(price__isnull=True).order_by('-price')
    page_config = {
        'title': '电源信息',
        'icon_class': 'fas fa-plug',
        'item_type': '电源'
    }
    context = {
        'items': power_supplies,
        'page_config': page_config
    }
    return render(request, 'dianyuan.html', context)

@login_required(login_url='/login/')
def about(request):
    context = {
        'username': request.user.username
    }
    return render(request, 'about.html', context)

@login_required(login_url='/login/')
def contact(request):
    context = {
        'username': request.user.username
    }
    return render(request, 'contact.html', context)

# 登录和注册视图不需要登录验证
def login(request):
    # 如果用户已登录，直接重定向到首页
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                return render(request, 'login.html', {'error': '用户名或密码错误'})
        except Exception as e:
            return render(request, 'login.html', {'error': '登录失败，请重试'})
            
    return render(request, 'login.html')

def register(request):
    # 如果用户已登录，直接重定向到首页
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': '用户名已存在'})
        
        try:
            User.objects.create_user(username=username, password=password)
            return redirect('login')
        except Exception as e:
            return render(request, 'register.html', {'error': '注册失败，请重试'})
            
    return render(request, 'register.html')

# 添加退出视图
def logout_view(request):
    logout(request)
    return redirect('login')

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

@login_required(login_url='/login/')
def get_memories(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        print("\n开始爬取内存数据...")
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='memory_')
        
        # 创建Edge浏览器选项
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        options.add_argument(f'--user-data-dir={temp_dir}')
        
        # 创建Edge浏览器实例
        driver = webdriver.Edge(options=options)
        # 最大化浏览器窗口
        driver.maximize_window()
        
        try:
            print("正在访问中关村在线内存页面...")
            driver.get("https://detail.zol.com.cn/memory/")
            time.sleep(3)
            
            print("清空现有内存数据...")
            Memory.objects.all().delete()
            
            page_num = 1
            max_pages = 20
            total_items = 0
            
            while page_num <= max_pages:
                print(f"\n正在处理第 {page_num} 页...")
                # 等待产品列表加载完成
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-follow-id^='p']"))
                    )
                except Exception as e:
                    print(f"等待产品列表加载失败: {e}")
                    time.sleep(5)
                
                # 滚动页面到底部以加载所有内容
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                products = soup.find_all('li', attrs={'data-follow-id': lambda x: x and x.startswith('p')})
                
                if not products:
                    print("未找到产品信息，可能页面结构有变化")
                    break
                
                print(f"在第 {page_num} 页找到 {len(products)} 个产品")
                
                for i, product in enumerate(products, 1):
                    try:
                        name_elem = product.find('h3').find('a')
                        name = name_elem.get('title', '未知名称')
                        
                        # 获取价格 - 更新价格获取逻辑
                        price_elem = product.find('span', class_='price-normal')
                        if price_elem:
                            price_type = price_elem.find('b', class_='price-type')
                            price = price_type.text if price_type else "暂无价格"
                        else:
                            price = "暂无价格"
                        
                        # 获取评分
                        score_elem = product.find('span', class_='score')
                        score = score_elem.text if score_elem else "暂无评分"
                        
                        # 获取评论数
                        comment_elem = product.find('a', class_='comment-num')
                        comment_count = comment_elem.text if comment_elem else "0人点评"
                        
                        # 清理价格并保存
                        cleaned_price = clean_price_for_db(price)
                        if cleaned_price:
                            Memory.objects.create(
                                name=name,
                                price=cleaned_price,
                                score=score,
                                comments=comment_count
                            )
                            total_items += 1
                            print(f"[{page_num}-{i}] 成功保存: {name} - {price} - 评分:{score} - {comment_count}")
                        else:
                            print(f"[{page_num}-{i}] 跳过无效价格产品: {name}")
                            
                    except Exception as e:
                        print(f"[{page_num}-{i}] 提取产品信息时出错: {e}")
                        continue
                
                if page_num == max_pages:
                    print("\n已达到指定的最大页数限制")
                    break
                
                # 查找并点击下一页按钮
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next"))
                    )
                    if "disabled" in next_button.get_attribute("class"):
                        print("已到达最后一页")
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"翻页失败或已到最后一页: {e}")
                    break
                    
        except Exception as e:
            print(f"\n爬取过程中出现错误: {e}")
            raise Exception(f"爬取内存数据失败: {str(e)}")
        finally:
            print("\n关闭浏览器...")
            try:
                driver.quit()
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")
            print(f"\n内存数据爬取完成，共保存 {total_items} 条记录")
            
    memories = Memory.objects.exclude(price__isnull=True).order_by('-price')
    page_config = {
        'title': '内存信息',
        'icon_class': 'fas fa-memory',
        'item_type': '内存'
    }
    context = {
        'items': memories,
        'page_config': page_config
    }
    return render(request, 'neicun.html', context)

@login_required(login_url='/login/')
def get_hard_disks(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        print("\n开始爬取硬盘数据...")
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix='hard_disk_')
        
        # 创建Edge浏览器选项
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        options.add_argument(f'--user-data-dir={temp_dir}')
        
        # 创建Edge浏览器实例
        driver = webdriver.Edge(options=options)
        # 最大化浏览器窗口
        driver.maximize_window()
        
        try:
            print("正在访问中关村在线硬盘页面...")
            driver.get("https://detail.zol.com.cn/hard_drives/")
            time.sleep(3)
            
            print("清空现有硬盘数据...")
            HardDisk.objects.all().delete()
            
            page_num = 1
            max_pages = 20
            total_items = 0
            
            while page_num <= max_pages:
                print(f"\n正在处理第 {page_num} 页...")
                # 等待产品列表加载完成
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-follow-id^='p']"))
                    )
                except Exception as e:
                    print(f"等待产品列表加载失败: {e}")
                    time.sleep(5)
                
                # 滚动页面到底部以加载所有内容
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                products = soup.find_all('li', attrs={'data-follow-id': lambda x: x and x.startswith('p')})
                
                if not products:
                    print("未找到产品信息，可能页面结构有变化")
                    break
                
                print(f"在第 {page_num} 页找到 {len(products)} 个产品")
                
                for i, product in enumerate(products, 1):
                    try:
                        name_elem = product.find('h3').find('a')
                        name = name_elem.get('title', '未知名称')
                        
                        # 获取价格 - 更新价格获取逻辑
                        price_elem = product.find('span', class_='price-normal')
                        if price_elem:
                            price_type = price_elem.find('b', class_='price-type')
                            price = price_type.text if price_type else "暂无价格"
                        else:
                            price = "暂无价格"
                        
                        # 获取评分
                        score_elem = product.find('span', class_='score')
                        score = score_elem.text if score_elem else "暂无评分"
                        
                        # 获取评论数
                        comment_elem = product.find('a', class_='comment-num')
                        comment_count = comment_elem.text if comment_elem else "0人点评"
                        
                        # 清理价格并保存
                        cleaned_price = clean_price_for_db(price)
                        if cleaned_price:
                            HardDisk.objects.create(
                                name=name,
                                price=cleaned_price,
                                score=score,
                                comments=comment_count
                            )
                            total_items += 1
                            print(f"[{page_num}-{i}] 成功保存: {name} - {price} - 评分:{score} - {comment_count}")
                        else:
                            print(f"[{page_num}-{i}] 跳过无效价格产品: {name}")
                            
                    except Exception as e:
                        print(f"[{page_num}-{i}] 提取产品信息时出错: {e}")
                        continue
                
                if page_num == max_pages:
                    print("\n已达到指定的最大页数限制")
                    break
                
                # 查找并点击下一页按钮
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next"))
                    )
                    if "disabled" in next_button.get_attribute("class"):
                        print("已到达最后一页")
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"翻页失败或已到最后一页: {e}")
                    break
                    
        except Exception as e:
            print(f"\n爬取过程中出现错误: {e}")
            raise Exception(f"爬取硬盘数据失败: {str(e)}")
        finally:
            print("\n关闭浏览器...")
            try:
                driver.quit()
                # 清理临时目录
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")
            print(f"\n硬盘数据爬取完成，共保存 {total_items} 条记录")
            
    hard_disks = HardDisk.objects.exclude(price__isnull=True).order_by('-price')
    page_config = {
        'title': '硬盘信息',
        'icon_class': 'fas fa-hdd',
        'item_type': '硬盘'
    }
    context = {
        'items': hard_disks,
        'page_config': page_config
    }
    return render(request, 'yingpan.html', context)

@login_required(login_url='/login/')
def get_power_supplies(request):
    if request.method == 'POST' and request.POST.get('action') == 'crawl':
        print("\n开始爬取电源数据...")
        
        # 创建Edge浏览器选项
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # 启用无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-component-update')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        
        # 创建Edge浏览器实例
        driver = webdriver.Edge(options=options)
        # 最大化浏览器窗口
        driver.maximize_window()
        
        try:
            print("正在访问中关村在线电源页面...")
            driver.get("https://detail.zol.com.cn/power/")
            time.sleep(3)
            
            print("清空现有电源数据...")
            PowerSupply.objects.all().delete()
            
            page_num = 1
            max_pages = 20
            total_items = 0
            
            while page_num <= max_pages:
                print(f"\n正在处理第 {page_num} 页...")
                # 等待产品列表加载完成
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-follow-id^='p']"))
                    )
                except Exception as e:
                    print(f"等待产品列表加载失败: {e}")
                    time.sleep(5)
                
                # 滚动页面到底部以加载所有内容
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                products = soup.find_all('li', attrs={'data-follow-id': lambda x: x and x.startswith('p')})
                
                if not products:
                    print("未找到产品信息，可能页面结构有变化")
                    break
                
                print(f"在第 {page_num} 页找到 {len(products)} 个产品")
                
                for i, product in enumerate(products, 1):
                    try:
                        name_elem = product.find('h3').find('a')
                        name = name_elem.get('title', '未知名称')
                        
                        # 获取价格 - 更新价格获取逻辑
                        price_elem = product.find('span', class_='price-normal')
                        if price_elem:
                            price_type = price_elem.find('b', class_='price-type')
                            price = price_type.text if price_type else "暂无价格"
                        else:
                            price = "暂无价格"
                        
                        # 获取评分
                        score_elem = product.find('span', class_='score')
                        score = score_elem.text if score_elem else "暂无评分"
                        
                        # 获取评论数
                        comment_elem = product.find('a', class_='comment-num')
                        comment_count = comment_elem.text if comment_elem else "0人点评"
                        
                        # 清理价格并保存
                        cleaned_price = clean_price_for_db(price)
                        if cleaned_price:
                            PowerSupply.objects.create(
                                name=name,
                                price=cleaned_price,
                                score=score,
                                comments=comment_count
                            )
                            total_items += 1
                            print(f"[{page_num}-{i}] 成功保存: {name} - {price} - 评分:{score} - {comment_count}")
                        else:
                            print(f"[{page_num}-{i}] 跳过无效价格产品: {name}")
                            
                    except Exception as e:
                        print(f"[{page_num}-{i}] 提取产品信息时出错: {e}")
                        continue
                
                if page_num == max_pages:
                    print("\n已达到指定的最大页数限制")
                    break
                
                # 查找并点击下一页按钮
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next"))
                    )
                    if "disabled" in next_button.get_attribute("class"):
                        print("已到达最后一页")
                        break
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"翻页失败或已到最后一页: {e}")
                    break
                    
        except Exception as e:
            print(f"\n爬取过程中出现错误: {e}")
            raise Exception(f"爬取电源数据失败: {str(e)}")
        finally:
            print("\n关闭浏览器...")
            try:
                driver.quit()
            except Exception as e:
                print(f"关闭浏览器时出错: {str(e)}")
            print(f"\n电源数据爬取完成，共保存 {total_items} 条记录")
            
    power_supplies = PowerSupply.objects.exclude(price__isnull=True).order_by('-price')
    for power_supply in power_supplies:
        if power_supply.price:
            power_supply.price = mark_safe(f"{power_supply.price}￥")
            
    page_config = {
        'title': '电源信息',
        'icon_class': 'fas fa-plug',
        'item_type': '电源'
    }
    context = {
        'items': power_supplies,
        'page_config': page_config
    }
    return render(request, 'dianyuan.html', context)


