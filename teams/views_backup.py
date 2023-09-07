from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests
from django.conf import settings
from datetime import datetime

TEAM_HITTER_HEADERS = settings.TEAM_HITTER_HEADERS
TEAM_PITCHER_HEADERS = settings.TEAM_PITCHER_HEADERS
PLAYER_PITCHER_HEADERS = settings.PLAYER_PITCHER_HEADERS
PLAYER_HITTER_HEADERS = settings.PLAYER_HITTER_HEADERS

STAT_CATEGORY = {
    "homeRuns": "HomeRuns",
    "strikeouts": "Strike Outs",
    "battingAverage": "Batting Average",
}

# Create your views here.

BASE_URL = "https://statsapi.mlb.com"
MLB_NEWS_URL = "https://dapi.cms.mlbinfra.com/v2/content/en-us/sel-mlb-news-list"


def home(request):
    response = requests.get(f"{BASE_URL}/api/v1/standings?leagueId=103,104")
    teams = response.json()["records"]
    template = loader.get_template("home.html")
    news = get_mlb_news()
    context = filter_teams(teams)
    context["news_display"] = news
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


def team(request, team_id, position):
    response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}/roster")
    roster = response.json()["roster"]
    template = loader.get_template("team.html")
    headers = TEAM_PITCHER_HEADERS if position == "pitcher" else TEAM_HITTER_HEADERS

    team_response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}")
    team = team_response.json()["teams"][0]

    players = []
    for player in roster:
        if position == "pitcher" and player["position"]["type"].lower() == "pitcher":
            stats = get_player_stats(player["person"]["id"], position)
            players.append(stats)
        elif position == "hitters" and player["position"]["type"].lower() != "pitcher":
            stats = get_player_stats(player["person"]["id"], position)
            players.append(stats)

    print("teaM >>", team)
    context = {
        "players": players,
        "headers": headers,
        "team_id": team_id,
        "team_name": team["name"],
        "position": position,
    }
    return HttpResponse(template.render(context, request))


def get_player_stats(person_id, position):
    response = requests.get(
        f"{BASE_URL}/api/v1/people/{person_id}?hydrate=stats(group=[hitting,pitching,fielding],type=[yearByYear])"
    )
    player_stats = response.json()["people"][0]
    # print("PLAYER >", player_stats)
    # player_stats["so_percentage"] = (
    #     player_stats["stats"][-1]["splits"][-1]["stat"]["strikeOuts"]
    #     / player_stats["stats"][-1]["splits"][-1]["stat"]["atBats"]
    # ) * 100

    stat_type = "pitching" if position == "pitcher" else "hitting"
    for stat in player_stats["stats"]:
        if stat["group"]["displayName"] == stat_type:
            player_stats["table_stats"] = stat["splits"]
            break
    return player_stats


def player(request, person_id, team_id, position):

    team_response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}")
    team = team_response.json()["teams"][0]
    stats = get_player_stats(person_id, position)
    template = loader.get_template("player.html")
    context = {
        "player_info": stats,
        "team_info": team,
        "position": position,
        "headers": PLAYER_HITTER_HEADERS
        if position == "hitters"
        else PLAYER_PITCHER_HEADERS,
    }
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


def get_mlb_news():
    response = requests.get(MLB_NEWS_URL)
    news_list = response.json()["items"][:4]
    news_display = []
    for news in news_list:
        news_display.append(
            {
                "headline": news["headline"],
                "created_by": news["createdBy"],
                "content_date": datetime.strptime(
                    news["contentDate"].split("T")[0], "%Y-%m-%d"
                ).strftime("%B %d, %Y"),
                "img_url": news["thumbnail"]["templateUrl"].replace(
                    "{formatInstructions}", "t_16x9/t_w1024/"
                ),
                "slug": news["slug"],
            }
        )
    return news_display


def leaderboard(request):

    response = requests.get(
        f"{BASE_URL}/api/v1/stats/leaders?leaderCategories=strikeouts,battingAverage,homeRuns"
        # f"{BASE_URL}/api/v1/stats/leaders?leaderCategories=homeRuns"
    )

    stat_list = response.json()["leagueLeaders"]
    context = {"stat_list": stat_list}

    template = loader.get_template("leaderboard.html")
    return HttpResponse(template.render(context, request))
