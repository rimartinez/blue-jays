from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests

# Create your views here.

BASE_URL = "https://statsapi.mlb.com"


def home(request):
    # response = requests.get(f"{BASE_URL}/api/v1/teams?sportId=1")
    response = requests.get(f"{BASE_URL}/api/v1/standings?leagueId=103,104")
    teams = response.json()["records"]
    template = loader.get_template("home.html")
    context = filter_teams(teams)
    return HttpResponse(template.render(context, request))


def filter_teams(teams):
    context = {
        "al_east": [],
        "nl_east": [],
        "al_central": [],
        "nl_central": [],
        "al_west": [],
        "nl_west": [],
    }
    for team in teams:
        if team["division"]["id"] == 200:
            context["al_west"] = team["teamRecords"]
        elif team["division"]["id"] == 201:
            context["al_east"] = team["teamRecords"]
        elif team["division"]["id"] == 202:
            context["al_central"] = team["teamRecords"]
        elif team["division"]["id"] == 203:
            context["nl_west"] = team["teamRecords"]
        elif team["division"]["id"] == 204:
            context["nl_east"] = team["teamRecords"]
        elif team["division"]["id"] == 205:
            context["nl_central"] = team["teamRecords"]
    return context


# def teams(request):
#     response = requests.get(f"{BASE_URL}/api/v1/teams?sportId=1")
#     teams = response.json()["teams"]
#     template = loader.get_template("teams.html")
#     context = {"teams": teams}
#     return HttpResponse(template.render(context, request))


def team(request, team_id):
    response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}/roster")
    roster = response.json()["roster"]
    template = loader.get_template("team.html")

    pitchers = []
    hitters = []
    for player in roster:
        print("PLATER>>", player)
        if player["position"]["type"].lower() == "pitcher":
            pitchers.append(player)
        else:
            hitters.append(player)

    context = {
        "pitchers": pitchers,
        "hitters": hitters,
        "team_id": team_id,
    }
    return HttpResponse(template.render(context, request))


def player(request, person_id):
    response = requests.get(
        f"{BASE_URL}/api/v1/people/{person_id}?hydrate=stats(group=[hitting,pitching,fielding],type=[yearByYear])"
    )
    person = response.json()["people"][0]
    get_career_batting_info(person)
    template = loader.get_template("player.html")
    context = {"info": person}
    return HttpResponse(template.render(context, request))


def get_career_batting_info(person):
    person["career_atbats"] = 0
    person["career_runs"] = 0
    person["career_hits"] = 0
    person["career_homeruns"] = 0
    person["career_rbi"] = 0
    person["career_stolenbases"] = 0
    person["career_hitsbypitch"] = 0
    person["career_baseonballs"] = 0
    person["career_sacflies"] = 0
    for stat in person["stats"]:
        for split in stat["splits"]:
            stat = split["stat"]
            person["career_atbats"] += stat["atBats"] if "atBats" in stat else 0
            person["career_runs"] += stat["runs"] if "runs" in stat else 0
            person["career_hits"] += stat["hits"] if "hits" in stat else 0
            person["career_homeruns"] += stat["homeRuns"] if "homeRuns" in stat else 0
            person["career_rbi"] += stat["rbi"] if "rbi" in stat else 0
            person["career_stolenbases"] += (
                stat["stolenBases"] if "stolenBases" in stat else 0
            )
            person["career_hitsbypitch"] += (
                stat["hitByPitch"] if "hitByPitch" in stat else 0
            )
            person["career_baseonballs"] += (
                stat["baseOnBalls"] if "baseOnBalls" in stat else 0
            )
            person["career_sacflies"] += stat["sacFlies"] if "sacFlies" in stat else 0

    person["career_avg"] = "{:.3f}".format(
        person["career_hits"] / person["career_atbats"]
    )
    person["career_obp"] = "{:.3f}".format(
        (
            person["career_hits"]
            + person["career_hitsbypitch"]
            + person["career_baseonballs"]
        )
        / (
            person["career_atbats"]
            + person["career_hitsbypitch"]
            + person["career_baseonballs"]
            + person["career_sacflies"]
        )
    )
