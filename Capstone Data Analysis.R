## Capstone Data Analysis
# Title: Assessing the Relationship Between Music-Sharing Tweet Popularity 
        #and Long-Term Spotify Streaming Popularity
# by Elizabeth Kiel

# Import track data
track.all = read.csv('C:/Users/eliza/Downloads/spotify/spotify_api/track_data.csv', header = TRUE)

# Check normality of response
par(mfrow=c(1,2))
hist(track.all$popularity, main = "Frequency of Popularity - All Tracks", xlab = "Popularity") # left-skewed
# Correct normality of response by removing popularity scores equal to 0
track.pop0 = subset(track.all, popularity>0)
hist(track.pop0$popularity, main = "Frequency of Popularity > 0", xlab = "Popularity")

# Fit the MLR model
full.mod = lm(popularity~frequency+reply_count+like_count+retweet_count+quote_count+following+followers+verified+follow_ratio+frequency, data = track.pop0)
summary(full.mod)

# Use the step-wise function for variable selection  
step(full.mod, direction="both", k=2)
# Model produced by step-wise function
step.mod = lm(popularity ~ frequency + reply_count + retweet_count + quote_count + 
                 following + followers + verified + follow_ratio, data = track.pop0)

# Examine the model diagnostic plots
par(mfrow=c(2,2))
plot(step.mod)
# Remove influential outlier points as identified 
track.pop0.outrm = track.pop0[-c(5396,84712,99447,99495,130081,117979),]

# Fit model again with influential points removed
full.mod2 = lm(popularity~frequency+reply_count+like_count+retweet_count+quote_count+following+followers+verified+follow_ratio+frequency, data = track.pop0.outrm)
step(full.mod2, direction="both", k=2)
step.mod2 = lm(popularity ~ frequency + reply_count + retweet_count + quote_count + 
                  following + followers + verified + follow_ratio, data = track.pop0.outrm)
summary(step.mod2)

# Normalize response variable with boxcox() function
library(MASS)
par(mfrow=c(1,1))
bc = boxcox(step.mod2)
lambda <- bc$x[which.max(bc$y)]
# Fit new linear regression model using the Box-Cox transformation
final.mod = lm(((popularity^lambda-1)/lambda) ~ frequency + reply_count + retweet_count + quote_count + 
                    following + followers + verified + follow_ratio, data = track.pop0.outrm)

# Step-wise regression with limit of second order model
step(final.mod.bc, .~.^2, direction="both", k=2)
# Fit the final model
final.mod.2 = lm(formula = ((popularity^lambda - 1)/lambda) ~ frequency + reply_count + 
                  retweet_count + quote_count + following + followers + verified + 
                  follow_ratio + frequency:follow_ratio + following:follow_ratio + 
                  frequency:followers + retweet_count:follow_ratio + frequency:verified + 
                  following:followers + followers:follow_ratio + frequency:following + 
                  retweet_count:following + verified:follow_ratio + frequency:quote_count + 
                  reply_count:quote_count + frequency:retweet_count + quote_count:followers, 
                data = track.pop0.outrm)

summary(final.mod.2)