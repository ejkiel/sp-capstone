#!/usr/bin/env python
# coding: utf-8

# # Capstone Data Collection
# by Elizabeth Kiel '23
# 
# In March 2022, Professor Eni Mustafaraj helped me to collect ~4 million tweets that contained the Spotify sharing link "open.spotify.com/" 
# 
# In the following code, tweets are randomly sampled, and their unique Spotify ID (nested in the sharing link) is extracted. The IDs are then passed to the Spotify API and all of the information is compiled and exported to a new JSON document. 

# ### A. Randomize tweet indices
# The twitter data files are of variable size so, to most efficiently take a random sample of the tweets, a list of all tweet indices was created.

# In[1]:


import json, os
import glob
import random


# Get the filenames of the Twitter data files.

# In[2]:


fileNames = glob.glob('C:/Users/eliza/Downloads/spotify/results_*.json')


# Get a list of all the tweet indices.

# In[4]:


allTweetIndexes = [] # list to store all indices

for file in fileNames: # for each file of tweets
    fileData = json.load(open(file)) # open each file
    for page in range(len(fileData)): # for each page of tweets
        tweets = fileData[page]['tweets'] # extract the tweets
        for tweet in range(len(tweets)): # for each tweet on the page
            tweetIndex = [file, page, tweet] # append the file, page, tweet #s
            allTweetIndexes.append(tweetIndex) # append to all tweet indices list


# Randomize the indices.

# In[5]:


rt = [] # list to sort random indices

for i in len(allTweetIndices): # for the length of all tweets
    randomIndex = random.randint(0,len(allTweetIndexes)) # get a random index
    tweetIndex = allTweetIndexes.pop(randomIndex) # pop the tweet at that index
    rt.append(tweetIndex) # append to random list


# ### B. Create functions to collect Spotify data
# Now that the indices have been randomized, the list can be iterated through to be extracted for its Spotify ID. The functions below aid in extracting the IDs

# In[7]:


def getURLs(tweet):
    """
    Returns a list of expanded URLs for a given tweet.
    """
    urlList = [] # empty list for return
    
    # for each url in the tweet entities
    for urlInd in range(len(tweet['entities']['urls'])):
        expandedURL = tweet['entities']['urls'][urlInd]['expanded_url']

        # if the url is a spotify link, add to list
        if 'open.spotify.com/track/' in expandedURL or 'open.spotify.com/album/' in expandedURL:
            urlList.append(expandedURL)
            
    return urlList


# In[8]:


def getSpotifyID(urls):
    """
    Returns the type of Spotify URL along with the ID in a tuple
    i.e., either ('track',trackID) or ('album',albumID)
    """
    for url in urls:
        # if the link is a Spotify track link
        if 'open.spotify.com/track/' in url:
            trackID = url.replace('https://open.spotify.com/track/', '').replace('http://open.spotify.com/track/', '').split('?')[0]
            return('track',trackID)
            
        # if the link is a Spotify album link
        if 'open.spotify.com/album/' in url:
            albumID = url.replace('https://open.spotify.com/album/', '').replace('http://open.spotify.com/album/', '').split('?')[0]
            return('album',albumID)


# In[ ]:


def getUserInfo(rt, userID):
    """
    Extract the twitter author information from the Twitter data set. 
    """
    userData = json.load(open(rt[0]))[rt[1]]['users']
    user_info = False
    while not user_info:
        for user in userData:
            if user['id'] == userID:
                user_info = True
                metrics = user['public_metrics']
                info_dict = {'following': metrics['following_count'],
                    'followers':  metrics['followers_count'],
                    'verified':  user['verified']}
    return info_dict


# ### C. Collect Spotify data
# Use the above functions and the Spotify API to collect the Spotify track/album data, and save/export with corresponding tweet data.

# Initialize Spotipy client.

# In[9]:


import spotipy, os
from spotipy.oauth2 import SpotifyOAuth
scope = "user-library-read"

# enter credentials and redirect URI
os.environ['SPOTIPY_CLIENT_ID'] = 'b122dd7f61644e0d811e697250f9d431'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'd1e52f72f5a3402984743bb985cc050a'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8889/callback'

# authorization
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
sp.trace = True # turn on tracing
sp.trace_out = True # turn on trace out


# Get 5,000 random tweet indices.

# In[10]:


randomTweets = rt[:5000]
rt = rt[5001:]


# In[11]:


save = [] # save every 5,000 tweets

for i in range(len(randomTweets)): # for all random tweets saved
    rt = randomTweets[i] # get the tweet index
    
    # get the relevant tweet & author data
    tweetData = json.load(open(rt[0]))[rt[1]]['tweets'][rt[2]]
    userID = tweetData['author_id']
    userInfo = getUserInfo(rt, userID)
    urls = getURLs(tweetData)
    
    # get the spotify ID and type
    sID = getSpotifyID(urls)
    try:
        if sID[0] == 'track': # get track info if track
            trackTag = f"spotify:track:{sID[1]}"
            trackInfo = sp.track(trackTag)
            info = [tweetData,trackInfo,userInfo]
            save.append(info) # get album info if album
        if sID[0] == 'album':
            albumTag = f"spotify:album:{sID[1]}"
            albumInfo = sp.album(albumTag)
            info = [tweetData,albumInfo,userInfo]
            save.append(info)
            
        # if the length of tweets = 500, export 
        if len(save) == 500:
            with open(f'C:/Users/eliza/Downloads/spotify/spotify_api/sdata_{fileNum}.json','w') as f:
                json.dump(save, f)
                fileNum += 1
                save = []
        if i == len(randomTweets) - 1: # if you reach the end, save
            with open(f'C:/Users/eliza/Downloads/spotify/spotify_api/sdata_{fileNum}.json','w') as f:
                json.dump(save, f)
    except:
        # sometimes the track/album with the given ID does not exist anymore
        # in this case, we can just pass... 
        pass


# Compile all of the data into readable file!

# In[1]:


import glob, json
fileNames = glob.glob('C:/Users/eliza/Downloads/spotify/spotify_api/sdata_*.json')
len(fileNames)


# In[2]:


allData = []
for file in fileNames:
    fileData = json.load(open(file))
    for datapt in fileData:
        allData.append(datapt)


# In[3]:


albumData = []
trackData = []

trackFreq = {}
albumFreq = {}


# In[4]:


for i in range(len(allData)):
    tweetID = allData[i][0]['id']
    reply_count = allData[i][0]['public_metrics']['reply_count']
    like_count = allData[i][0]['public_metrics']['like_count']
    quote_count = allData[i][0]['public_metrics']['quote_count']
    popularity = allData[i][1]['popularity']
    mediaID = allData[i][1]['id']
    following = allData[i][2]['following']
    followers = allData[i][2]['followers']
    verified = allData[i][2]['verified']
    if followers != 0:
        follow_ratio = following/followers
    else:
        follow_ratio = 0
        
    save_data = {'tweetID': tweetID, 'reply_count': reply_count,
                'like_count': like_count, 'quote_count': quote_count,
                'popularity': popularity, 'mediaID': mediaID,
                'following': following, 'followers': followers,
                'verified': verified, 'follow_ratio': follow_ratio}

    if 'track_number' not in allData[i][1].keys(): # if album,
        if mediaID not in albumFreq.keys():
            albumFreq[mediaID] = 1
        else:
            albumFreq[mediaID] += 1
        albumData.append(save_data)
    else:
        if mediaID not in trackFreq.keys():
            trackFreq[mediaID] = 1
        else:
            trackFreq[mediaID] += 1
        trackData.append(save_data)


# In[5]:


with open(f'C:/Users/eliza/Downloads/spotify/spotify_api/albumFreq.json','w') as f:
    json.dump(albumFreq, f)
    
with open(f'C:/Users/eliza/Downloads/spotify/spotify_api/trackFreq.json','w') as f:
    json.dump(trackFreq, f)


# In[6]:


td_final = []
for i in range(len(trackData)):
    trackInfo = trackData[i]
    tID = trackInfo['mediaID']
    freq = trackFreq[tID]
    trackInfo['frequency'] = freq
    td_final.append(trackInfo)


# In[7]:


ad_final = []
for i in range(len(albumData)):
    albumInfo = albumData[i]
    aID = albumInfo['mediaID']
    freq = albumFreq[aID]
    albumInfo['frequency'] = freq
    ad_final.append(albumInfo)


# In[8]:


with open(f'C:/Users/eliza/Downloads/spotify/spotify_api/track_data_final.json','w') as f:
    json.dump(td_final, f)
    
with open(f'C:/Users/eliza/Downloads/spotify/spotify_api/album_data_final.json','w') as f:
    json.dump(ad_final, f)


# In[9]:


import pandas as pd

track_df = pd.DataFrame(td_final)
track_df.to_csv('C:/Users/eliza/Downloads/spotify/spotify_api/track_data_final.csv')

album_df = pd.DataFrame(ad_final)
album_df.to_csv('C:/Users/eliza/Downloads/spotify/spotify_api/album_data_final.csv')

