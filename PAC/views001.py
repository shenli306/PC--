from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from PAC.models import CPU, GraphicsCard, Motherboard, Memory, HardDisk, PowerSupply
from django.db.models import Avg

@login_required(login_url='/login/')
def see(request):
    """数据可视化大屏视图"""
    # 获取各类硬件的有效数量（只统计有价格的数据）
    cpu_count = CPU.objects.filter(price__isnull=False).count()
    gpu_count = GraphicsCard.objects.filter(price__isnull=False).count()
    board_count = Motherboard.objects.filter(price__isnull=False).count()
    memory_count = Memory.objects.filter(price__isnull=False).count()
    disk_count = HardDisk.objects.filter(price__isnull=False).count()
    power_count = PowerSupply.objects.filter(price__isnull=False).count()

    # 添加调试信息
    print("Debug - Counts:", {
        'cpu': cpu_count,
        'gpu': gpu_count,
        'board': board_count,
        'memory': memory_count,
        'disk': disk_count,
        'power': power_count
    })

    # 计算各类硬件的平均价格
    cpu_avg_price = CPU.objects.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0
    gpu_avg_price = GraphicsCard.objects.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0
    board_avg_price = Motherboard.objects.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0
    memory_avg_price = Memory.objects.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0
    disk_avg_price = HardDisk.objects.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0
    power_avg_price = PowerSupply.objects.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0

    # 添加调试信息
    print("Debug - Avg Prices:", {
        'cpu': cpu_avg_price,
        'gpu': gpu_avg_price,
        'board': board_avg_price,
        'memory': memory_avg_price,
        'disk': disk_avg_price,
        'power': power_avg_price
    })

    # 获取各品牌硬件数量（只统计有价格的数据）
    brand_counts = {
        'cpu': {
            'Intel': CPU.objects.filter(name__icontains='Intel', price__isnull=False).count(),
            'AMD': CPU.objects.filter(name__icontains='AMD', price__isnull=False).count(),
        },
        'gpu': {
            'NVIDIA': GraphicsCard.objects.filter(name__icontains='NVIDIA', price__isnull=False).count(),
            'AMD': GraphicsCard.objects.filter(name__icontains='AMD', price__isnull=False).count(),
            'ASUS': GraphicsCard.objects.filter(name__icontains='华硕', price__isnull=False).count(),
            'GIGABYTE': GraphicsCard.objects.filter(name__icontains='技嘉', price__isnull=False).count(),
            'MSI': GraphicsCard.objects.filter(name__icontains='微星', price__isnull=False).count(),
        },
        'memory': {
            'ADATA': Memory.objects.filter(name__icontains='威刚', price__isnull=False).count(),
            'Samsung': Memory.objects.filter(name__icontains='三星', price__isnull=False).count(),
        },
        'disk': {
            'Samsung': HardDisk.objects.filter(name__icontains='三星', price__isnull=False).count(),
            'Seagate': HardDisk.objects.filter(name__icontains='希捷', price__isnull=False).count(),
        },
        'board': {
            'ASUS': Motherboard.objects.filter(name__icontains='华硕', price__isnull=False).count(),
            'GIGABYTE': Motherboard.objects.filter(name__icontains='技嘉', price__isnull=False).count(),
            'MSI': Motherboard.objects.filter(name__icontains='微星', price__isnull=False).count(),
        },
        'power': {
            'MSI': PowerSupply.objects.filter(name__icontains='微星', price__isnull=False).count(),
        }
    }

    context = {
        'username': request.user.username,
        'cpu_count': cpu_count,
        'gpu_count': gpu_count,
        'board_count': board_count,
        'memory_count': memory_count,
        'disk_count': disk_count,
        'power_count': power_count,
        'cpu_avg_price': round(cpu_avg_price, 2),
        'gpu_avg_price': round(gpu_avg_price, 2),
        'board_avg_price': round(board_avg_price, 2),
        'memory_avg_price': round(memory_avg_price, 2),
        'disk_avg_price': round(disk_avg_price, 2),
        'power_avg_price': round(power_avg_price, 2),
        'brand_counts': brand_counts,
        'intel_cpu': brand_counts['cpu']['Intel'],
        'amd_cpu': brand_counts['cpu']['AMD'],
        'nvidia_gpu': brand_counts['gpu']['NVIDIA'],
        'amd_gpu': brand_counts['gpu']['AMD'],
        'asus_gpu': brand_counts['gpu']['ASUS'],
        'gigabyte_gpu': brand_counts['gpu']['GIGABYTE'],
        'msi_gpu': brand_counts['gpu']['MSI'],
        'adata_memory': brand_counts['memory']['ADATA'],
        'samsung_memory': brand_counts['memory']['Samsung'],
        'samsung_disk': brand_counts['disk']['Samsung'],
        'seagate_disk': brand_counts['disk']['Seagate'],
        'asus_board': brand_counts['board']['ASUS'],
        'gigabyte_board': brand_counts['board']['GIGABYTE'],
        'msi_board': brand_counts['board']['MSI'],
        'msi_power': brand_counts['power']['MSI'],
    }

    # 添加调试信息
    print("Debug - Context:", context)

    return render(request, 'see.html', context)
