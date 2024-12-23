from django.db import models
from django import forms
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.conf import settings
import json
import xml.etree.ElementTree as ET
import os


# Create your models here.
class Sale(models.Model):
    date = models.DateField()  # Дата продажи
    product = models.CharField(max_length=100)  # Название продукта
    quantity = models.IntegerField()  # Количество товара
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена товара
    save_to_db = models.BooleanField(default=True)  # Флаг сохранения в БД

    def __str__(self):
        return f"Продукт: {self.product}, Количество: {self.quantity}, Цена: {self.price}"

    class Meta:
        # Уникальная комбинация значений для предотвращения дублирования
        unique_together = ('date', 'product', 'quantity', 'price')