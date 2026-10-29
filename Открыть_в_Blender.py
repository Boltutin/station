"""
Скрипт для открытия модели station_pavilion.glb в Blender и сохранения в .blend
Запуск:
1. Откройте Blender
2. Перейдите во вкладку Scripting -> Open -> выберите этот файл -> нажмите Run Script
Или в командной строке:
blender --python Открыть_в_Blender.py
"""

import bpy
import os

# Очистка начальной сцены (куб, камера, свет)
bpy.ops.wm.read_factory_settings(use_empty=True)

# Путь к нашему файлу GLB
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else r"I:\DVGUPS\7_semestr\Моделирование виртуальной и дополненной реальности\2_Проект_WebXR_Приложение"
glb_path = os.path.join(current_dir, "station_pavilion.glb")
blend_path = os.path.join(current_dir, "station_pavilion.blend")

if os.path.exists(glb_path):
    print(f"Импорт модели: {glb_path}")
    bpy.ops.import_scene.gltf(filepath=glb_path)
    
    # Сохранение в родной формат Blender .blend
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Успешно сохранен файл проекта Blender: {blend_path}")
else:
    print(f"Файл {glb_path} не найден!")
