# Twitter BotNet

First, you need create a Twitter developer account, create a Twitter App/Project and setup all the API crendential and tokens.
Download browser driver that match your browser version. (Edge browser driver has been tested).
Setup your bot accounts. For example, you have 5 Twitter bot accounts, then add them into init.py "Bot_List"
Then run the command as the following:
```
python Twitter_BotNet.py "elonmusk" "MSG" "D:\\PIC\\test.jpeg"
```
The script will automatically register your 5 bot accounts to your Twitter App/Project then the script can drive your bot accounts to reply all the elonmusk's followers' latest timeline with your custom message and picture. 
