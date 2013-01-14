import epub
from genshi.template import TemplateLoader

class Section:

    def __init__(self):
        self.title = ''
        self.subsections = []
        self.css = ''
        self.text = []
        self.templateFileName = 'ez-section.html'

class Book:

    def __init__(self):
        self.impl = epub.EpubBook()
        self.title = ''
        self.authors = []
        self.cover = ''
        self.lang = 'en-US'
        self.sections = []
        self.templateLoader = TemplateLoader('templates')

    def __addSection(self, section, id, depth):
        if depth > 0:
            stream = self.templateLoader.load(section.templateFileName).generate(section = section)
            html = stream.render('xhtml', doctype = 'xhtml11', drop_xml_decl = False)
            item = self.impl.addHtml('', '%s.html' % id, html)
            self.impl.addSpineItem(item)
            self.impl.addTocMapNode(item.destPath, section.title, depth)
            id += '.'
        if len(section.subsections) > 0:
            for i, subsection in enumerate(section.subsections):
                self.__addSection(subsection, id + str(i + 1), depth + 1)

    def make(self, outputDir):
        outputFile = outputDir + '.epub'

        self.impl.setTitle(self.title)
        self.impl.setLang(self.lang)
        for author in self.authors:
            self.impl.addCreator(author)
        if self.cover:
            self.impl.addCover(self.cover)
        self.impl.addTitlePage()
        self.impl.addTocPage()
        root = Section()
        root.subsections = self.sections
        self.__addSection(root, 's', 0)
        self.impl.createBook(outputDir)
        self.impl.createArchive(outputDir, outputFile)
        #self.impl.checkEpub('epubcheck-1.0.5.jar', outputFile)
