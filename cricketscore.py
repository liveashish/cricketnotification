#!/usr/bin/env python2
import requests
from bs4 import BeautifulSoup
import pynotify
import re
from time import 

SLEEP_INTERVAL = 60

def getResponceFromURL(url):
    r = requests.get(url)
    while not r.ok:
            r = requests.get(url)
    return r

def sendmessage(title, message):
    pynotify.init("Test")
    notice = pynotify.Notification(title, message)
    notice.show()
    return 

def getRequiredMatchFromLiveGames(): 
    url = "http://static.cricinfo.com/rss/livescores.xml"
    r = getResponceFromURL(url)
    soup = BeautifulSoup(r.text)
    data = soup.find_all("title")
    #Get Titles of All Match (Includes runs also) and Retain only Team Names.
    #Live games title information starts from data[1]
    for gamenum,game in enumerate(data[1:]):
        print gamenum+1,re.sub(r'\s+'," ",re.sub('[^A-Za-z ]+', '', game.text))
    choice=input("Game number :")
    #Guid Tag in the xml contains the json id from which website refreshes data.
    jsonLink = soup.find_all("guid")[choice-1].text
    jsonLink = re.search(r'\d+',jsonLink).group()
    liveFeed= "http://www.espncricinfo.com/ci/engine/match/%s.json"%jsonLink
    return liveFeed

def getPlayingTeamNames(liveFeed):
    #Get the playing team names and store it in teamId:teamName dict format
    r = getResponceFromURL(liveFeed)
    playingTeams=dict()
    for team in r.json().get("team"):
        playingTeams[team.get("team_id")] = team.get("team_name")
    return playingTeams

def getScores(innings):
    #Get team names from the team ids. Get score information .
    #Prepare the title and score info to display
    batting_team_id=innings.get("batting_team_id")
    battingTeamName = playingTeams[batting_team_id]
    
    bowling_team_id=innings.get("bowling_team_id")
    bowlingTeamName = playingTeams.get(bowling_team_id)
    
    runs=innings.get("runs")
    overs = innings.get("overs")
    wickets = innings.get("wickets")
    runRate=innings.get("run_rate")
    title = "%s vs %s"%(battingTeamName,bowlingTeamName)
    score = "%s/%s from %s overs \n RunRate : %s"%(runs,wickets,overs,runRate)
    return (title,score)

def notifyScores(liveFeed,playingTeams):
    while True:
        r=getResponceFromURL(liveFeed)
        innings=r.json().get("live").get("innings")
        (title,score) = getScores(innings)
        sendmessage(title,score)
        sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    liveFeed=getRequiredMatchFromLiveGames()
    playingTeams = getPlayingTeamNames(liveFeed)
    notifyScores(liveFeed,playingTeams)