from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests
from django.conf import settings
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import inflect

P = inflect.engine()

PLAYER_PITCHER_HEADERS = settings.PLAYER_PITCHER_HEADERS
PLAYER_HITTER_HEADERS = settings.PLAYER_HITTER_HEADERS
DIVISION_NAMES = settings.DIVISION_NAMES


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
    al_east = []
    nl_east = []
    al_central = []
    nl_central = []
    al_west = []
    nl_west = []
    for team in teams:
        if team["division"]["id"] == 200:
            al_west = {
                "name": "AL West",
                "team_info": team["teamRecords"],
                "league_id": team["league"]["id"],
                "division_id": team["division"]["id"],
            }
        elif team["division"]["id"] == 201:
            al_east = {
                "name": "AL East",
                "team_info": team["teamRecords"],
                "league_id": team["league"]["id"],
                "division_id": team["division"]["id"],
            }
        elif team["division"]["id"] == 202:
            al_central = {
                "name": "AL Central",
                "team_info": team["teamRecords"],
                "league_id": team["league"]["id"],
                "division_id": team["division"]["id"],
            }
        elif team["division"]["id"] == 203:
            nl_west = {
                "name": "NL West",
                "team_info": team["teamRecords"],
                "league_id": team["league"]["id"],
                "division_id": team["division"]["id"],
            }
        elif team["division"]["id"] == 204:
            nl_east = {
                "name": "NL East",
                "team_info": team["teamRecords"],
                "league_id": team["league"]["id"],
                "division_id": team["division"]["id"],
            }
        elif team["division"]["id"] == 205:
            nl_central = {
                "name": "NL Central",
                "team_info": team["teamRecords"],
                "league_id": team["league"]["id"],
                "division_id": team["division"]["id"],
            }

    context = {
        "divisions": [al_east, nl_east, al_central, nl_central, al_west, nl_west],
    }
    return context


def team(request, team_id, league_id, division_id):
    response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}/roster")
    roster = response.json()["roster"]
    template = loader.get_template("team.html")

    pitchers = []
    hitters = []
    out_fielders = []
    in_fielders = []
    exec_list = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for player in roster:
            exec_list.append(executor.submit(get_people_info, player["person"]["id"]))

        for exec in exec_list:
            info = exec.result()
            if info["primaryPosition"]["type"] == "Pitcher":
                pitchers.append(info)
            elif info["primaryPosition"]["type"] == "Hitter":
                hitters.append(info)
            elif info["primaryPosition"]["type"] == "Infielder":
                in_fielders.append(info)
            elif info["primaryPosition"]["type"] == "Outfielder":
                out_fielders.append(info)

    context = {
        "player_groups": [
            {"position": "Pitchers", "players": pitchers},
            {"position": "Hitters", "players": hitters},
            {"position": "In Fielders", "players": in_fielders},
            {"position": "Out Fielders", "players": out_fielders},
        ],
        "team_id": team_id,
    }
    get_team_standing(team_id, league_id, division_id, context)
    return HttpResponse(template.render(context, request))


def get_people_info(id):
    info_response = requests.get(f"{BASE_URL}/api/v1/people/{id}")
    return info_response.json()["people"][0]


def get_player_stats(person_id):
    response = requests.get(
        f"{BASE_URL}/api/v1/people/{person_id}?hydrate=stats(group=[hitting,pitching,fielding],type=[yearByYear])"
    )
    player_stats = response.json()["people"][0]

    stat_type = (
        "pitching"
        if player_stats["primaryPosition"]["name"] == "Pitcher"
        else "hitting"
    )
    for stat in player_stats["stats"]:
        if stat["group"]["displayName"] == stat_type:
            player_stats["table_stats"] = [
                split for split in stat["splits"] if "team" in split
            ]
            break
    return player_stats


def player(request, person_id, team_id):

    team_response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}")
    team = team_response.json()["teams"][0]
    stats = get_player_stats(person_id)
    template = loader.get_template("player.html")
    context = {
        "player_info": stats,
        "team_info": team,
        "headers": PLAYER_PITCHER_HEADERS
        if stats["primaryPosition"]["name"] == "Pitcher"
        else PLAYER_HITTER_HEADERS,
    }
    return HttpResponse(template.render(context, request))


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
    )
    context = {"stat_list": response.json()["leagueLeaders"]}
    template = loader.get_template("leaderboard.html")
    return HttpResponse(template.render(context, request))


def get_team_standing(team_id, league_id, division_id, context):
    response = requests.get(f"{BASE_URL}/api/v1/standings?leagueId={league_id}")
    record_list = response.json()["records"]
    for record_data in record_list:
        if record_data["division"]["id"] == division_id:
            for team in record_data["teamRecords"]:
                if team["team"]["id"] == team_id:
                    record = get_team_division_standing(team, division_id)
                    context[
                        "standing"
                    ] = f"{P.ordinal(team['divisionRank'])} in {DIVISION_NAMES[record['division']['name']]}"
                    context[
                        "record"
                    ] = f"{record['wins']} - {record['losses']} ({record['pct']})"
                    context["gamesback"] = team["divisionGamesBack"]
                    context["team_name"] = team["team"]["name"]


def get_team_division_standing(team, division_id):
    for record in team["records"]["divisionRecords"]:
        if record["division"]["id"] == division_id:
            return record
