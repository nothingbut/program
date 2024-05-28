import json

class BookShelfConfig:

    configFile = '/Users/shichang/Workspace/program/data/bsconfig.json'

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        with open(self.configFile) as f:
            config = json.load(f)
        return config

    def get_config(self):
        return self.config
    
    def getTemplateFile(self):
        return self.config.get('env.templateFile')
    
    def getCSSFile(self):
        return self.config.get('env.cssFile')
    
    def getTargetFile(self):
        return self.config.get('env.targetFile')
    
    def getCoverPath(self):
        return self.config.get('env.coverPath')
    
    def getBookDB(self):
        return self.config.get('source.bookDB')
    
    def getBookDetailQuery(self):
        return self.config.get('source.bookDetailQuery')
   
    def getTextSubjectList(self):
        return self.config.get('parser.textSubjectList')
    
    def getTextEndingList(self):
        return self.config.get('parser.textEndingList')
    
    def getSourcePath(self):
        return self.config.get('source.sourcePath')
    
    def getTagsJson(self):
        return self.config.get('attr.tagsJson')
    
    def getChapterHeaderTemplate(self):
        return self.config.get('gen.chapterHeaderTemplate')
    
    def getContentLineTemplate(self):
        return self.config.get('gen.contentLineTemplate')
    
if __name__ == '__main__':
    bsconfig = BookShelfConfig()
    print(bsconfig.getTagsJson())