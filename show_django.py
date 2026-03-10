import os

def print_tree(startpath, max_level=3):
    # Папки, которые полностью скрываем
    exclude_dirs = {'__pycache__', '.git', '.vscode', '.idea', 'node_modules', '.DS_Store'}
    # Папки, которые показываем, но не углубляемся
    shallow_dirs = {'venv', 'env', '.venv', 'virtualenv'}
    # Важные файлы, которые всегда показываем
    important_files = {'manage.py', 'requirements.txt', 'pyproject.toml', 
                      'settings.py', 'urls.py', 'wsgi.py', 'asgi.py',
                      'package.json', 'webpack.config.js', 'dockerfile', 'docker-compose.yml'}
    
    print("🌳 СТРУКТУРА DJANGO ПРОЕКТА 🌳\n")
    
    for root, dirs, files in os.walk(startpath):
        # Определяем уровень вложенности
        level = root.replace(startpath, '').count(os.sep)
        if level > max_level:
            continue
        
        # Полностью исключаем ненужные папки
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Определяем отступ
        if level == 0:
            prefix = ""
        else:
            indent = "│   " * (level - 1)
            prefix = indent + ("└── " if level == 1 else "├── ")
        
        # Печатаем текущую папку
        folder_name = os.path.basename(root) if level > 0 else os.path.basename(os.path.abspath(startpath))
        
        # Проверяем, это venv или обычная папка
        if folder_name in shallow_dirs:
            print(f"{prefix}📁 {folder_name}/  [VIRTUAL ENV - содержимое скрыто]")
            dirs.clear()  # Не заходим внутрь venv
            continue
        else:
            # Определяем специальные иконки для папок
            folder_icon = "📁"  # обычная папка
            
            # Проверяем специальные папки
            if folder_name.lower() in ['static', 'staticfiles']:
                folder_icon = "📦"
            elif folder_name.lower() in ['media', 'images', 'img', 'photos', 'uploads']:
                folder_icon = "🖼️ "
            elif folder_name.lower() in ['templates', 'templatetags']:
                folder_icon = "🌐"
            elif folder_name.lower() in ['js', 'javascript', 'scripts']:
                folder_icon = "⚡"
            elif folder_name.lower() in ['css', 'styles', 'stylesheets']:
                folder_icon = "🎨"
            elif folder_name == 'migrations':
                folder_icon = "🗃️ "
            elif any(x in folder_name.lower() for x in ['app', 'api', 'users', 'blog', 'shop']):
                folder_icon = "🚀"
            
            print(f"{prefix}{folder_icon} {folder_name}/")
        
        # Показываем файлы в текущей папке
        file_prefix = "│   " * level + "├── "
        last_file_prefix = "│   " * level + "└── "
        
        # Группируем файлы по типам
        py_files = [f for f in files if f.endswith('.py')]
        html_files = [f for f in files if f.endswith(('.html', '.htm'))]
        css_files = [f for f in files if f.endswith('.css')]
        js_files = [f for f in files if f.endswith('.js')]
        image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.bmp', '.webp', '.tiff'))]
        other_important = [f for f in files if f in important_files or f.endswith(('.json', '.yml', '.yaml', '.md', '.txt', '.env', '.sql', '.pdf'))]
        
        # Все файлы для сортировки
        all_files_to_show = []
        
        # Добавляем Python файлы
        for file in sorted(py_files):
            # Пропускаем служебные файлы только на глубоких уровнях
            if file in ['__init__.py', '__pycache__']:
                continue
            if file == 'apps.py' and level > 2:
                continue
            all_files_to_show.append(("🐍", file))
        
        # Добавляем HTML файлы
        for file in sorted(html_files):
            all_files_to_show.append(("🌐", file))
        
        # Добавляем CSS файлы
        for file in sorted(css_files):
            all_files_to_show.append(("🎨", file))
        
        # Добавляем JavaScript файлы
        for file in sorted(js_files):
            all_files_to_show.append(("⚡", file))
        
        # Добавляем изображения (первые 3)
        for i, file in enumerate(sorted(image_files)):
            if i < 3:  # Показываем только первые 3 изображения
                all_files_to_show.append(("🖼️ ", file))
        
        # Добавляем остальные важные файлы
        for file in sorted(other_important):
            if any(file in group for _, group in [("🐍", py_files), ("🌐", html_files), ("🎨", css_files), ("⚡", js_files), ("🖼️ ", image_files)]):
                continue
            icon = "📄"  # по умолчанию
            if file.endswith('.json'):
                icon = "📋"
            elif file.endswith(('.yml', '.yaml')):
                icon = "⚙️ "
            elif file.endswith('.md'):
                icon = "📝"
            elif file.endswith('.sql'):
                icon = "🗄️ "
            elif file.endswith('.pdf'):
                icon = "📕"
            all_files_to_show.append((icon, file))
        
        # Показываем все файлы
        for i, (icon, file) in enumerate(all_files_to_show):
            current_prefix = last_file_prefix if i == len(all_files_to_show) - 1 else file_prefix
            print(f"{current_prefix}{icon} {file}")
        
        # Показываем количество скрытых изображений
        if len(image_files) > 3:
            print(f"{last_file_prefix}🖼️  ... и еще {len(image_files) - 3} изображений")
        
        # Если это venv или достигли максимального уровня - не идем глубже
        if folder_name in shallow_dirs or level == max_level:
            dirs.clear()

if __name__ == "__main__":
    print_tree('.', max_level=3)  # Изменил на 3 уровня!
    print("\n" + "="*70)
    print("📁 - обычная папка")
    print("📦 - статические файлы (static)")
    print("🖼️  - папка с изображениями")
    print("🌐 - папка шаблонов (templates)")
    print("⚡ - папка JavaScript")
    print("🎨 - папка CSS стилей")
    print("🗃️  - миграции")
    print("🚀 - приложение Django")
    
    print("\n🐍 - Python файл")
    print("🌐 - HTML файл")
    print("🎨 - CSS файл")
    print("⚡ - JavaScript файл")
    print("🖼️  - изображение")
    print("📄 - конфигурационный файл")
    print("📋 - JSON файл")
    print("⚙️  - YAML конфиг")
    print("📝 - документация")
    print("🗄️  - база данных")
    print("="*70)