from django import forms
from django.db import models
from django import forms
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.conf import settings
import json
import xml.etree.ElementTree as ET
import os
from .models import Sale

from django import forms
from .models import Sale

class SalesForm(forms.ModelForm):  # Наследуем от ModelForm
    class Meta:
        model = Sale
        fields = ['date', 'product', 'quantity', 'price', 'save_to_db']  # Укажите нужные поля модели


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Выберите файл (JSON или XML)")

class SearchForm(forms.Form):
    query = forms.CharField(label="Поиск", required=False)

def save_to_files(data):
    folder = os.path.join(settings.BASE_DIR, 'sales_data')
    os.makedirs(folder, exist_ok=True)

    # Save to JSON
    json_path = os.path.join(folder, 'sales.json')
    if not os.path.exists(json_path):
        with open(json_path, 'w') as f:
            json.dump([], f)

    with open(json_path, 'r') as f:
        try:
            sales = json.load(f)
            if not isinstance(sales, list):
                sales = []
        except json.JSONDecodeError:
            sales = []

    sales.append(data)
    with open(json_path, 'w') as f:
        json.dump(sales, f, indent=4, ensure_ascii=False)

    # Save to XML
    xml_path = os.path.join(folder, 'sales.xml')
    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
    else:
        root = ET.Element('Sales')
        tree = ET.ElementTree(root)

    sale = ET.Element('Sale')
    for key, value in data.items():
        ET.SubElement(sale, key).text = str(value)
    root.append(sale)
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
