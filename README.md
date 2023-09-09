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
   for MacOS using homebrew
   ```
   $ brew install pyenv-virutalenv
   ```
   for Windows
   
3. Install python version using pyenv
   ```
   $ pyenv install 3.11.0
   ```
4. Create virtual environment
   ```
   $ pyenv virtualenv 3.11.0 env1
   ```
5. Download project files
   ```
   $ git clone git@github.com:rimartinez/blue-jays.git
   ```
   ```
   $ cd blue-jays
   ```
6. Install dependency
   ```
   $ pip install -r requirements.txt
   ```

## How to run
1. Run django project
   ```
   $ python manage.py runserver 0:8000
   ```
