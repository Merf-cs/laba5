import os
import json
import xml.etree.ElementTree as ET
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from .forms import SalesForm, UploadFileForm
from django.http import JsonResponse
from django.db import models
from django import forms
import json
import xml.etree.ElementTree as ET
import os
from .models import Sale
from django.shortcuts import render, redirect, get_object_or_404

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

# Функция сохранения данных в JSON и XML
def save_sales_data(data):
    folder = os.path.join(settings.BASE_DIR, 'sales_data')
    os.makedirs(folder, exist_ok=True)

    # путь JSON
    json_path = os.path.join(folder, 'sales.json')

    # создаём файл, если его нет
    if not os.path.exists(json_path):
        with open(json_path, 'w') as f:
            json.dump([], f)
    try:
        with open(json_path, 'r') as f:
            try:
                sales = json.load(f)
                if not isinstance(sales, list):  # Если данные не список, сбрасываем
                     sales = []
            except json.JSONDecodeError:
                sales =[] # Если файл повреждён
    
        # Добавляем новые данные
        sales.append(data)

        # Записываем данные обратно в файл
        with open(json_path, 'w') as f:
            json.dump(sales, f, indent=4, ensure_ascii=False)
    
    except Exception as e:
        print (f"Ошибка при работе с файлом JSON: {e}")

    # XML
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


# Форма добавления данных
def sales_form(request):
    if request.method == 'POST':
        form = SalesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data.pop('save_to_db'):
                # Check for duplicates
                if not Sale.objects.filter(**data).exists():
                    Sale.objects.create(**data)
                else:
                    return render(request, 'sales/sales_form.html', {
                        'form': form,
                        'error': 'Запись уже существует в базе данных!'
                    })
            else:
                save_to_files(data)
            return redirect('sales_list')
    else:
        form = SalesForm()
    return render(request, 'sales/sales_form.html', {'form': form})


# Функция загрузки файлов
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            folder = os.path.join(settings.BASE_DIR, 'sales_data')
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, file.name)

            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Валидация загруженного файла
            if file.name.endswith('.json'):
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    os.remove(file_path)
                    return render(request, 'sales/upload_file.html', {'form': form, 'error': 'Невалидный JSON-файл!'})
            elif file.name.endswith('.xml'):
                try:
                    ET.parse(file_path)
                except ET.ParseError:
                    os.remove(file_path)
                    return render(request, 'sales/upload_file.html', {'form': form, 'error': 'Невалидный XML-файл!'})

            return redirect('sales_list')
    else:
        form = UploadFileForm()
    return render(request, 'sales/upload_file.html', {'form': form})


# Вывод списка данных
def sales_list(request):
    source = request.GET.get('source', 'files')
    sales = []
    if source == 'db':
        sales = Sale.objects.all()
    else:
        folder = os.path.join(settings.BASE_DIR, 'sales_data')
        json_path = os.path.join(folder, 'sales.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                try:
                    sales = json.load(f)
                except json.JSONDecodeError:
                    sales = []
    return render(request, 'sales/sales_list.html', {'sales': sales, 'source': source})

def search_sales(request):
    query = request.GET.get('query', '')  # Получаем запрос поиска из параметра 'query'
    if query:
        sales = Sale.objects.filter(product__icontains=query)  # Ищем товары, содержащие запрос
    else:
        sales = Sale.objects.all()  # Если поисковый запрос пуст, показываем все записи
    sales_list = list(sales.values())  # Преобразуем QuerySet в список словарей
    return JsonResponse(sales_list, safe=False)

    
def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)  # Получаем запись или возвращаем ошибку 404
    if request.method == 'POST':
        form = SalesForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('sales_list')  # Перенаправление на список после сохранения
    else:
        form = SalesForm(instance=sale)  # Заполняем форму существующими данными
    return render(request, 'sales/edit_sale.html', {'form': form, 'sale': sale})

def delete_sale(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    sale.delete()
    return redirect('sales_list')

def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)  # Используем get_object_or_404 для получения записи
    if request.method == 'POST':
        form = SalesForm(request.POST, instance=sale)  # Передаем instance для редактирования
        if form.is_valid():
            form.save()  # Сохраняем изменения
            return redirect('sales_list')  # Перенаправляем на список продаж
    else:
        form = SalesForm(instance=sale)  # Для GET запроса создаем форму с данными существующей записи
    return render(request, 'sales/edit_sale.html', {'form': form, 'sale': sale})