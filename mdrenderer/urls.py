from django.urls import path
from editor import views

urlpatterns = [
    path('', views.editor_view, name='editor'),
    path('render/', views.render_markdown, name='render_markdown'),
    path('export/md/', views.export_md, name='export_md'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
