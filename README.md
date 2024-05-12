# FCBot - Football Competition Bot

WORK IN PROGRESS!

Discord bot for hosting prediction contests for football tournaments with your friends. Predictions are submitted one day at a time. 

## Functionality
Implemented functionality:
- Retrieve match data from [football-data.org](https://www.football-data.org/)
- Command to show upcoming match day. 

Todo:
- Commands for user input of predictions for next match day (started)
    - Potentially allow for prediction of more matches. 
- Create local database for matches, predictions and scores
- Implement scoring system that updates whenever matches are finished
- Command to display rankings
- Set up automatic user pings for predictions
- Command for changing competition and season

## Running the bot

### Clone repository

Clone repository:
```
git clone https://github.com/Habarug/FCBot.git
```

Install requirements:
```
cd FCBot
pip install -r requirments.txt
```

### Update discord token and football-data API key

- Make a copy of [FCBot/config/PRIVATE_TEMPLATE.json5] and name it PRIVATE.json5. 
- [Make a Discord Bot application](https://discord.com/developers/applications/1222618661949407286/bot) and copy the token into PRIVATE.json5. 
- Register at [football-data](https://www.football-data.org/client/register) (free tier is fine), and copy the key into PRIVATE.json5. 

### Run the bot

```
python FCBot
```