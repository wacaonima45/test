from django.http import HttpResponse
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'School Management System API'
        return context


def home_simple(request):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>School Management System API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #4CAF50;
                padding-bottom: 10px;
            }
            .links {
                margin-top: 20px;
            }
            .links a {
                display: inline-block;
                margin: 10px;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .links a:hover {
                background: #45a049;
            }
            .info {
                background: #e7f3fe;
                border-left: 6px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏫 School Management System API</h1>
            <p>Добро пожаловать в API системы управления школой. Используйте следующие ссылки:</p>

            <div class="info">
                <strong>Для тестирования API используйте:</strong>
                <ul>
                    <li>Swagger UI - интерактивная документация API</li>
                    <li>ReDoc - альтернативная документация</li>
                    <li>Панель администратора Django</li>
                </ul>
            </div>

            <div class="links">
                <a href="/swagger/">Swagger UI</a>
                <a href="/redoc/">ReDoc Documentation</a>
                <a href="/admin/">Admin Panel</a>
                <a href="/api/">API Root</a>
            </div>

            <div style="margin-top: 30px; color: #666;">
                <h3>📚 Доступные эндпоинты:</h3>
                <ul>
                    <li><code>/api/auth/</code> - Аутентификация (Djoser)</li>
                    <li><code>/api/teachers/</code> - Учителя</li>
                    <li><code>/api/students/</code> - Ученики</li>
                    <li><code>/api/classrooms/</code> - Кабинеты</li>
                    <li><code>/api/school-classes/</code> - Классы</li>
                    <li><code>/api/schedules/</code> - Расписание</li>
                    <li><code>/api/reports/</code> - Отчеты</li>
                </ul>
            </div>

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 0.9em;">
                <p>Лабораторная работа 3. Реализация серверной части на Django REST Framework</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)