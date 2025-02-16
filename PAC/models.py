from django.db import models
from django.core.validators import MinValueValidator

class CPU(models.Model):
    name = models.CharField(max_length=200, verbose_name='CPU名称')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='价格',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    score = models.CharField(max_length=50, verbose_name='评分')
    comments = models.CharField(max_length=50, verbose_name='评论数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='爬取时间')
    brand = models.CharField(max_length=50, verbose_name='品牌', blank=True)
    series = models.CharField(max_length=50, verbose_name='系列', blank=True)

    def save(self, *args, **kwargs):
        # 确保price字段为数字
        if self.price and not isinstance(self.price, (int, float, str)):
            try:
                self.price = float(self.price)
            except (ValueError, TypeError):
                self.price = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'CPU'
        verbose_name_plural = 'CPU列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class GraphicsCard(models.Model):
    name = models.CharField(max_length=200, verbose_name='显卡名称')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='价格',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    score = models.CharField(max_length=50, verbose_name='评分')
    comments = models.CharField(max_length=50, verbose_name='评论数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='爬取时间')
    brand = models.CharField(max_length=50, verbose_name='品牌', blank=True)
    memory_size = models.CharField(max_length=50, verbose_name='显存大小', blank=True)

    def save(self, *args, **kwargs):
        if self.price and not isinstance(self.price, (int, float, str)):
            try:
                self.price = float(self.price)
            except (ValueError, TypeError):
                self.price = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '显卡'
        verbose_name_plural = '显卡列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Motherboard(models.Model):
    name = models.CharField(max_length=200, verbose_name='主板名称')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='价格',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    score = models.CharField(max_length=50, verbose_name='评分')
    comments = models.CharField(max_length=50, verbose_name='评论数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='爬取时间')
    brand = models.CharField(max_length=50, verbose_name='品牌', blank=True)
    chipset = models.CharField(max_length=50, verbose_name='芯片组', blank=True)

    def save(self, *args, **kwargs):
        if self.price and not isinstance(self.price, (int, float, str)):
            try:
                self.price = float(self.price)
            except (ValueError, TypeError):
                self.price = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '主板'
        verbose_name_plural = '主板列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Memory(models.Model):
    name = models.CharField(max_length=200, verbose_name='内存名称')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='价格',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    score = models.CharField(max_length=50, verbose_name='评分')
    comments = models.CharField(max_length=50, verbose_name='评论数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='爬取时间')
    capacity = models.CharField(max_length=50, verbose_name='容量', blank=True)
    frequency = models.CharField(max_length=50, verbose_name='频率', blank=True)

    def save(self, *args, **kwargs):
        if self.price and not isinstance(self.price, (int, float, str)):
            try:
                self.price = float(self.price)
            except (ValueError, TypeError):
                self.price = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '内存'
        verbose_name_plural = '内存列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class HardDisk(models.Model):
    name = models.CharField(max_length=200, verbose_name='硬盘名称')
    description = models.TextField(blank=True, verbose_name='描述')
    specifications = models.TextField(blank=True, verbose_name='规格')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='价格',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    score = models.CharField(max_length=50, verbose_name='评分')
    comments = models.CharField(max_length=50, verbose_name='评论数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='爬取时间')

    def save(self, *args, **kwargs):
        if self.price and not isinstance(self.price, (int, float, str)):
            try:
                self.price = float(self.price)
            except (ValueError, TypeError):
                self.price = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '硬盘'
        verbose_name_plural = '硬盘列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class PowerSupply(models.Model):
    name = models.CharField(max_length=200, verbose_name='电源名称')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='价格',
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    score = models.CharField(max_length=50, verbose_name='评分')
    comments = models.CharField(max_length=50, verbose_name='评论数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='爬取时间')

    def save(self, *args, **kwargs):
        if self.price and not isinstance(self.price, (int, float, str)):
            try:
                self.price = float(self.price)
            except (ValueError, TypeError):
                self.price = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '电源'
        verbose_name_plural = '电源列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
