import webbrowser
f = open('links.txt', 'r')
for link in f:
    webbrowser.open(link, new=2) #opens link in new tab of default browser
f.close()
