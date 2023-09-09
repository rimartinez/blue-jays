# Project Blue-Jays


## About The Project

This is a simple Django project that displays:
* MLB divisional rankings
* Team page with roster
* Player page with info
* Stats Leaderboards


## Built With
* [Python Django Framework](https://www.djangoproject.com/)


## Pre-requisites
* A Linux System - [CentOS](https://www.centos.org/) or MacOS
* [pyenv virtualenv](https://github.com/pyenv/pyenv-virtualenv)

## Installation
1. Install pyenv virtualenv  
   a. for MacOS using homebrew
   ```
   brew install pyenv-virutalenv
   ```
   b. for Windows  
   [Link for steps](https://github.com/pyenv/pyenv-virtualenv)
   
2. Install python version using pyenv
   ```
   pyenv install 3.11.0
   ```
3. Create virtual environment
   ```
   pyenv virtualenv 3.11.0 env1
   ```
4. Activate virtual environment
   ```
   pyenv activate env1
   ```
5. Download project files
   ```
   git clone https://github.com/rimartinez/blue-jays.git
   ```
   ```
   cd blue-jays
   ```

6. Install dependencies
   ```
   pip install -r requirements.txt
   ```

## How to run
Note: always activate virutal environment before running the project
1. Access project folder
   ```
   cd blue-jays
   ```
2. Run project
   ```
   python manage.py runserver 0:8000
   ```
   If for some reason you want to change the port, you might need to open the port you want in firewall settings
   ```
   sudo firewall-cmd --zone=public --add-port=<port number you want>/tcp --permanent
   ```
   ```
   firewall-cmd --reload
   ```


## Improvements
* Create a database to store information and not call mlb api everytime  
&nbsp;- It will have faster response time if database is local  
&nbsp;- Thought there might be an issue with this as it needs to get updated everytime for records, standings and stats leaderboard to display updated information
* Put all styles in css file
* Add error handlings. A few are:
  - MLB api returns 404 or other status code
  - Checking of keys in the dictionary returned by API
* Can add caching in api for faster response time.

## Notes
* For the home page, I decided to display the whole team name as the info I have from the api I used does not have abbreviation and I think it is not worth because of the response time to call each team's api for it.
* For the player page, I displayed all players in all positions instead of having a toggle for hitter and pitcher. I thought that it would be easier for the user if they can see every player in one page
* A bit confused on how stats leaderboard api works because in "homerun" category there is "hitting", "pitching" and "catching" stat group.
  I just displayed all 3 stat group in 3 separate tables

