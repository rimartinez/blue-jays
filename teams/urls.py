from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("team/<int:team_id>/roster/<str:position>", views.team, name="team"),
    path(
        "player/<int:person_id>/<int:team_id>/<str:position>",
        views.player,
        name="player",
    ),
]
