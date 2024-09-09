import json, os

class BookShelfConfig:

    configFile = '/Users/shichang/Workspace/program/data/bsconfig.json'

    def __init__(self):
        self.config = self.load_config()
        self.osname = os.name

    def load_config(self):
        with open(self.configFile) as f:
            config = json.load(f)
        return config

    def get_config(self):
        return self.config
    
    def getTemplateFile(self):
        return self.config.get('.'.join([self.osname,'env.templateFile']))
    
    def getCSSFile(self):
        return self.config.get('.'.join([self.osname,'env.cssFile']))
    
    def getTargetFile(self):
        return self.config.get('.'.join([self.osname,'env.targetFile']))
    
    def getSourcePath(self):
        return self.config.get('.'.join([self.osname,'env.sourcePath']))
    
    def getTargetPath(self):
        return self.config.get('.'.join([self.osname,'env.targetPath']))

    def getCoverPath(self):
        return self.config.get('.'.join([self.osname,'env.coverPath']))
    
    def getCachePath(self):
        return self.config.get('.'.join([self.osname,'env.cachePath']))

    def getBookShelf(self):
        return self.config.get('.'.join([self.osname,'env.bookShelf']))
    
    def getBookDB(self):
        return self.config.get('.'.join([self.osname,'source.bookDB']))

    def getBookDBUrl(self):
        return self.config.get("source.yousuu")
    
    def getBookDetailQuery(self):
        return self.config.get('source.bookDetailQuery')
   
    def getTextSubjectList(self):
        return self.config.get('parser.textSubjectList')
    
    def getTextEndingList(self):
        return self.config.get('parser.textEndingList')
    
    def getStartString(self):
        return self.config.get('parser.htmlStartgStr')
    
    def getEndString(self):
        return self.config.get('parser.htmlEndStr')

    def getTagsJson(self):
        return self.config.get('attr.tagsJson')
    
    def getSourceList(self):
        return self.config.get('attr.sourcesites')
    
    def getChapterHeaderTemplate(self):
        return self.config.get('gen.chapterHeaderTemplate')
    
    def getContentLineTemplate(self):
        return self.config.get('gen.contentLineTemplate')
    
    def getPandocHeader(self):
        with open(self.config.get('.'.join([self.osname,'gen.pandocHeaderTemplate']))) as fp:
            return fp.read()
    
if __name__ == '__main__':
    bsconfig = BookShelfConfig()
    print(bsconfig.getTagsJson())