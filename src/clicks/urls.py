from django.urls import path

from clicks import views

app_name = 'clicks'
urlpatterns = [
    # ex: /clicks/campaign/5/
    path("campaign/<int:campaign>/", views.campaign_clicks, name='campaign'),
]
