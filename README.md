# Twitter-Stalker-v2
An improvement to the scrapy weekend project - this bot will scrap the Twitter v2 API to "stalk" accounts sending a Discord webhook if the "stalked" account has followed any new accounts

This Twitter Stalker Bot an improvement to the original Bot; the goal being to introduce new features and increase its extensibility for future suggested features.
It now now utilises mySQL, pickling data, further exploring Twitter API's and alongside further performance enhancements. It has also been improved to work at the limit of the Twitter API.

Additional mySQL data entry was integrated with the help of [Programming with Mosh](https://www.youtube.com/watch?v=7S_tz1z_5bA&ab_channel=ProgrammingwithMosh)

The bot also removes dependencies on Replit and its platform and refactoring to be used on any web server. 
The bot can now support a few hundred accounts from just 10 accounts.

Useful documentation: <br>
https://discordpy.readthedocs.io/en/stable/index.html <br>
https://developer.twitter.com/en/docs/twitter-api


Usage:
$meow to test if the bot is still alive
$twitter stalk all to manually check if any stalked accounts have followed new accounts
