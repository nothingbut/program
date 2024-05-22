const os = require('os');
const fs = require('fs');
const requests = require('requests');

const MP3File = require('mp3_tagger').MP3File;
const { VERSION_1, VERSION_2, VERSION_BOTH } = require('mp3_tagger');

function checkartist(all, artists) {
    let result = 0;
    for (let artist of all) {
        if (artists.includes(artist.name)) {
            result += 1;
        }
    }
    return result === artists.length;
}

function initquery(filter) {
    const qstring = `http://localhost:3000/cloudsearch?keywords=${filter.replace('')}`;
    const x = requests.get(qstring);
    const result = JSON.parse(x.text).result;
    if (result === null || result === {} || result.songCount === 0) {
        console.log(`can not find song from ${filter}`);
        return null;
    }
    return result;
}

function findtrack(result, title, artists, albumname) {
    if (result === null) {
        return 0;
    }
    let track = 0;
    for (let song of result.songs) {
        if (song.name !== title) {
            continue;
        }
        if (!checkartist(song.ar, artists)) {
            continue;
        }
        const album = song.al;
        if (album.name !== albumname) {
            console.log(`album name (${album.name}) not match with ${albumname}`);
        }
        const x = requests.get(`http://localhost:3000/album?id=${album.id}`);
        const songs = JSON.parse(x.text).songs;
        for (let index = 0; index < songs.length; index++) {
            if (songs[index].name === title) {
                track = index + 1;
                break;
            }
        }
        if (track > 0) {
            return track;
        }
    }
    return track;
}

function savetrack(mp3, track) {
    mp3.track = String(track);
    mp3.save();
    return track;
}

function addtrack(mp3file) {
    console.log(`processing on .. ${mp3file}`);
    const mp3 = new MP3File(mp3file);
    mp3.set_version(VERSION_2);
    const tags = mp3.get_tags();
    if (tags.song === null) {
        console.log(`${mp3file} is invalid mp3, or missing key tags`);
        return -1;
    }
    if (tags.track !== null) {
        return -1;
    }
    const song = tags.song.replace('\x00', '');
    const album = tags.album.replace('\x00', '');
    const artists = tags.artist.replace('\x00', '').split('、');
    console.log(`fix track ... ${mp3file} with tags ${tags}`);
    let result = initquery(artists.join('') + ' ' + song);
    let track = findtrack(result, song, artists, album);
    if (track !== 0) {
        return savetrack(mp3, track);
    }
    result = initquery(song);
    track = findtrack(result, song, artists, album);
    if (track !== 0) {
        return savetrack(mp3, track);
    }
    result = initquery(artists.join(''));
    track = findtrack(result, song, artists, album);
    if (track !== 0) {
        return savetrack(mp3, track);
    }
    return track;
}

const appendix = "mp3";
const root = '/Users/shichang/Downloads/temp/石头/';
const candidates = [];
candidates.push(root);
let index = 0;
while (index < candidates.length) {
    const path = candidates[index];
    const dirs = fs.readdirSync(path);
    console.log(`process ${path}`);
    for (let file of dirs) {
        const cur = path + file;
        if (fs.statSync(cur).isDirectory()) {
            candidates.push(cur + '/');
            console.log(`add ${cur}`);
        }
        if (file.endsWith(appendix)) {
            if (addtrack(cur) === 0) {
                console.log(`no track info find for ${file}`);
            }
        }
    }
    index += 1;
}
console.log(candidates);

