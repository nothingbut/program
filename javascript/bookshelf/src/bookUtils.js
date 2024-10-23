class bookEntity {
    constructor(book, rootpath) {
        this.id = book.NovelID;
        this.title = book.NovelName;
        this.author = book.Author;
        this.categories = book.categories;
        this.cover = book.BookImg;
        this.brief = book.brief;
        this.volumes = book.volumes;

        this.approot = rootpath;
        this.root = rootpath + 'chm/' + this.id;
        this.temp = rootpath + 'temp/' + this.id;
        this.coverfile = this.temp + '/cover.html';
        this.genpath = rootpath + 'gen/';
    }

    initPath() {
        var fs = require('fs');
        for (idx in this.categories) {
            this.genpath += this.categories[idx] + '/';
            if (!fs.existsSync(this.genpath)) {
                fs.mkdirSync(this.genpath);
            }
        }
        if (fs.existsSync(this.temp)) {
            this.cleanUp(this.temp);
        }
        fs.mkdirSync(this.temp);
        fs.copyFileSync(this.approot + 'templ/epubgen/main.css', this.temp + '/main.css');
    }

    buildCover() {
        var fs = require('fs');
        fs.copyFileSync(this.root + '/' + this.cover, this.temp + '/' + this.cover);
        var coverContent = fs.readFileSync(this.approot + 'templ/epubgen/cover.html', 'utf8');
        coverContent = coverContent.replaceAll('{title}', this.title).replaceAll('{author}', this.author).replaceAll('{cover}', this.cover).replaceAll('{brief}', this.brief);
        fs.writeFileSync(this.coverfile, coverContent);
    }

    async createEpub(target) {
        const spine = ['cover.html'];
        const toc = [[{ label: '封面', href: 'cover.html'}]];

        const withvolume = (this.volumes.length > 1) ? true : false;
        
        for (idx in this.volumes) {
            var tocItem = {};
            var vol = this.volumes[idx];
            if (withvolume) {
                var volumefile = this.prepareVolume(vol, idx);
                spine.push(volumefile);
                tocItem = [{ label: vol.title, href: volumefile}];
            }

            for (var ch in vol.chapters) {
                var chapterfile = this.prepareChapter(vol.chapters[ch]);
                spine.push(chapterfile);
                if (withvolume) {
                    tocItem.push([{ label: vol.chapters[ch].Title, href: chapterfile}]);
                }
                else {
                    toc.push({ label: vol.chapters[ch].Title, href: chapterfile});
                }
            }

            if (withvolume) {
                toc.push(tocItem);
            }
        }

        const options = {
            contentDir: this.temp,
            spine,
            toc,
            cover: this.cover,
            simpleMetadata: {
                author: this.author,
                title: this.title,
                language: 'zh-CN'
            }
        };
        
        const { EPUBCreator } = require('@eit6609/epub-creator');

        const creator = new EPUBCreator(options);
        await creator.create(target).then(data => {
            this.cleanUp(this.temp);
        }).catch((error) => console.log(error));
    }

    prepareVolume(volume) {
        var fs = require('fs');
        var filename = idx + '_' + volume.title + '.html'
        var volumefile = this.temp + '/' + filename;
        var content = fs.readFileSync(this.approot + 'templ/epubgen/volume.html', 'utf8');
        content = content.replaceAll('{volume}', volume.title).replaceAll('{first}', volume.chapters[0].Title).replaceAll('{last}', volume.chapters[volume.chapters.length - 1].Title);
        fs.writeFileSync(volumefile, content);
        return filename;
    }

    prepareChapter(chapter) {
        var contentstart = '<!--BookContent Start-->';
        var contentend = '<!--BookContent End-->';

        var fs = require('fs');
        var filename = chapter.id + '.html'
        var chptfile = this.temp + '/' + filename;
        var content = fs.readFileSync(this.approot + 'templ/epubgen/chapter.html', 'utf8');
        var material = fs.readFileSync(this.root + '/' + chapter.id + '.htm');
        var iconv = require('iconv-lite');
        material = iconv.decode(material, 'gbk');
        material = this.clearContent(material.substring(material.indexOf(contentstart) + contentstart.toString().length, material.indexOf(contentend)));
        content = content.replaceAll('{title}', chapter.Title).replaceAll('{content}', material);
        fs.writeFileSync(chptfile, content, 'utf8');
        return filename;
    }

    clearContent(text) {
        var newline = '</p><p>';
        return text.replaceAll('[\x01-\x1F,\x7F]', '').replaceAll('&nbsp;&nbsp;', '　')
            .replaceAll('<br>', newline).replaceAll('</br>', newline).replaceAll('<br >',newline)
            .replaceAll('<BR>', newline).replaceAll('<br />', newline).replaceAll('<P>', newline)
            .replaceAll('()','').replaceAll('<center>','').replaceAll('</center>','')
            .replaceAll('&#39;','\'').replaceAll('&amp;','&');
    }
   
    cleanUp(dirPath) {
        var fs = require('fs');
        const dir = fs.readdirSync(dirPath);
        dir.forEach(child => {
            const childPath = `${dirPath}/${child}`;
            if (fs.statSync(childPath).isDirectory()) {
                this.cleanUp(childPath);
            } else {
                fs.unlinkSync(childPath);
            }
        });
        fs.rmdirSync(dirPath);
    }

    async buildEpub() {
        this.initPath();

        var target = this.genpath + this.title + '.epub';
        var fs = require('fs');
        if (fs.existsSync(target)) {
            return 'Book ' + target + ' existed';
        }
        this.buildCover();
        this.createEpub(target);
        return 'Generate ' + target +' success';
    }
}

module.exports = function (data) {
    return new bookEntity(data);
}

module.exports.bookEntity = bookEntity;