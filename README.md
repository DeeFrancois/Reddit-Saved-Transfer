# Reddit-Saved-Transferer
A tool for transferring posts from your Reddit Saved list to another account/personal subreddit.

(_.exe version coming soon_)

<sup>Disclaimer: This is technically ready for public use as I don't plan on simplifying the GUI, but it still has some major bugs to fix and I've yet to clean up the code. It works well enough for me to use it regularly though, so I figured I'd upload it.</sup>

![demo](https://raw.githubusercontent.com/DeeFrancois/Reddit-Saved-Transfer/master/DocumentationImages/demo.png)

# Motivation
I found out a while ago that your Saved list on Reddit isn't infinite so I made this so I could transfer some of my saves to a different account. 
While working on this I noticed reddit doesn't have much functionality for sorting/browsing your saved list so that also became a part of it.

# Features
- Automated transferring of posts to another account
- Automated transferring of posts to a subreddit
- Scroll through the last 1000 posts in your saved list (API Limit, but when you unsave a post you can see even older saves)
- Hotlinks so you can open a post in your browser
- Thumbnail previews
- Sorting filters
- Drop down menu that shows all of the subreddits in your saved list (can be used for filtering)
- Video Players (both VLC and Python-MPV)
- Subreddit feed retrieval (100 posts from new/hot/top)
- Extract a text file containing a list of saved posts that were later deleted

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
- The "Extract List" button is for making a txt file with a list of posts that were later deleted by the user/moderators
