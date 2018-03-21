full_tweet = "SEP: Probabilistic Causation https://t.co/Y8MwSQ1kzT #philosophy"

broken_tweet = full_tweet.split(" ")
del broken_tweet[0]
del broken_tweet[len(broken_tweet)-1]
del broken_tweet[len(broken_tweet)-1]
print(broken_tweet)
title = ""
for i in range (0, len(broken_tweet)-1):
    title = title + broken_tweet[i] + '+'
title = title + broken_tweet[len(broken_tweet)-1]
print(title)

#this code segment will be used to parse @peoppenheimer's tweet.text
