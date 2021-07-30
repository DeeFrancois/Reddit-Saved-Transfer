# Reddit-Saved-Transfer
A tool for transferring posts from your Reddit Saved list to another account/personal subreddit

<sup>*Ready for public use as I don't plan on simplifying, but still has some major bugs to fix and I've yet to clean up the code. It works enough for me to use it regularly though, so I figured I'd upload it</sup>

![demo](https://raw.githubusercontent.com/DeeFrancois/Reddit-Saved-Transfer/master/DocumentationImages/demo.png)

# Motivation
I found out a while ago that your Reddit Saved List isn't infinite. So I initially made this so I could transfer some of my saves to a different account. 
Then I noticed reddit doesn't have much functionality for sorting/browsing your saved list so that also became a part of it.

# Features
- Scroll through the last 1000 posts in your saved list (API Limit, but when you unsave a post you can see even older saves)
- Hotlinks so you can open the post in your browser
- Thumbnail previews
- Sort saved list by SFW/NSFW and by Subreddit
- Drop down menu that shows all of the subreddits in your saved list (can be used for filtering)
- Video Player (Powered by python-mpv and Youtube-DL)
- Pull last 100 posts (hot/top/new) from a Subreddit 
- Automated transfering of posts to another account
- Automated transferring of posts to a subreddit

# How to Use (May have to just make a video..)

- You must first register a Reddit Application for each account you plan on logging in to: https://www.reddit.com/prefs/apps 
- Download awthemes and place into the same folder as the .py file: https://sourceforge.net/projects/tcl-awthemes/
- Now you can run the program, log in, and click Pull Saves at the top (this may take some time depending on your internet)
- Once logged in you can scroll through your saves, click on the thumbnail to select it and it will move to the middle or right click to hide it
- Here you can click to unsave if you'd like or transfer to the second account if you've logged it in
- You can also enable the Video Player and click the center thumbnail to play the video (scroll wheel for volume, left click to pause)
- Click Start to begin automatic loop for transferring the saves (speed limited by API) 
- Click the arrow at the top to change direction of transfer
- If using "Transfer to Subreddit" mode make sure to select the subreddit by entering it in the top bar on the receiving account and clicking "Select Sub"
- Click the Posting As button to change which account to post as
- The Refresh button is for applying filters
- Top/Hot/New only works if you've clicked Pull Subreddit instead of Pull Saves with a subreddit entered in the top bar
