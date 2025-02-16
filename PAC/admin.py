from django.contrib import admin
from .models import CPU, GraphicsCard, Motherboard, Memory, HardDisk, PowerSupply

@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'score', 'comments', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    list_per_page = 20
    ordering = ('-created_at',)

@admin.register(GraphicsCard)
class GraphicsCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'score', 'comments', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    list_per_page = 20
    ordering = ('-created_at',)

@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'score', 'comments', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    list_per_page = 20
    ordering = ('-created_at',)

@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'score', 'comments', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    list_per_page = 20
    ordering = ('-created_at',)

@admin.register(HardDisk)
class HardDiskAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'score', 'comments', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'specifications')
    list_per_page = 20
    ordering = ('-created_at',)

@admin.register(PowerSupply)
class PowerSupplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'score', 'comments', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    list_per_page = 20
    ordering = ('-created_at',)
