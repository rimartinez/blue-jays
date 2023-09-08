from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("team/<int:team_id>/roster", views.team, name="team"),
    path(
        "player/<int:person_id>/<int:team_id>",
        views.player,
        name="player",
    ),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]
