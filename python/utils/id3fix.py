import os, sys, requests, json
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH

def checkartist(all, artists):
    result = 0
    for artist in all:
        if artist.get('name') in artists:
            result += 1
    return result == len(artists)

def initquery(filter):
    qstring = 'http://localhost:3000/cloudsearch?keywords=%s' % filter.replace('#','')[0:50]
    x = requests.get(qstring)
    result = json.loads(x.text).get('result')
    if (result is None) or (result == {}) or (result.get('songCount') == 0):
        print('can not find song from %s' % filter)
        return None
    return result

def findtrack(result, title, artists, albumname):
    if result == None:
        return 0
    track = 0
    for song in result.get('songs'):
        if (song.get('name') != title):
            continue
        if not checkartist(song.get('ar'), artists):
            continue
        album = song.get('al')
        if album.get('name') != albumname:
            print('album name (%s) not match with %s' % (album.get('name'), albumname))

        x = requests.get('http://localhost:3000/album?id=%d' % album.get('id'))
        songs = json.loads(x.text).get('songs')
        for index in range(len(songs)):
            if songs[index].get('name') == title:
                track = index + 1
                break
        if (track > 0):
            return track
    return track

def savetrack(mp3, track):
#    print('save track as %d for %s' % (track, mp3.get_tags()))
    mp3.track = str(track)
    mp3.save()
    return track

def addtrack(mp3file):
    print('processing on .. %s' % mp3file)
    mp3 = MP3File(mp3file)
    mp3.set_version(VERSION_2)
    tags = mp3.get_tags()
    if (tags.get('song') is None):
        print('%s is invalid mp3, or missing key tags' % mp3file)
        return -1
    if (tags.get('track') is not None):
        return -1
    song = tags.get('song').replace('\x00','')
    album = tags.get('album').replace('\x00','')
    artists = tags.get('artist').replace('\x00','').split('、')
    
    print("fix track ... %s with tags %s", (mp3file, tags))
    result = initquery(' '.join(artists) + '' + ' ' + song)
    track = findtrack(result, song, artists, album)
    if (track != 0):
        return savetrack(mp3, track)

    result = initquery(song)
    track = findtrack(result, song, artists, album)
    if (track != 0):
        return savetrack(mp3, track)

    result = initquery(' '.join(artists))
    track = findtrack(result, song, artists, album)
    if (track != 0):
        return savetrack(mp3, track)
    return track

#addtrack('/Users/shichang/Music/take/take/月夏寻星计划/Girl - NuclearBomb牛客帮.mp3')


appendix = "mp3"
root = '/Users/shichang/Downloads/temp/FromMac/'
candidates = []
candidates.append(root)
index = 0
while (index < len(candidates)):
    path = candidates[index]
    dirs = os.listdir(path)
    print('process %s' % path)
    for file in dirs:
        cur = path + file
        if (os.path.isdir(cur)):
            candidates.append(cur + '/')
            print('add %s' % cur)
        if (file.endswith(appendix)):
            if (addtrack(cur) == 0):
                print('no track info find for %s' % file)
    index += 1
    
print(candidates)
