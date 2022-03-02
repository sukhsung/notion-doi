import re
import os
from habanero import Crossref
cr = Crossref()
Crossref(mailto = os.environ["mailto"])

class author :
    def __init__( self, given, family ) :
        given = self.check_author_given(given)
        self.given = given
        self.family = family
        self.fix_caps_family()

    def check_author_given( self, given ): 

        given = given.replace(".", ". ")
        given = re.sub(' +', ' ', given)
        if given[-1] == " ":
            given = given[:-1]
        return given

    def fix_caps_family( self ):
        family = self.family.title()
        if family[0:8] == 'Van Der ':
            family = 'van der ' + family[8:]
        elif family[0:4] == 'Van ':
            family = 'van ' + family[4:]

        self.family = family



    def given_abbrev( self ):
        #First, Check for dash 
        
        if self.given.split('-') == -1 :
            given = self.given
        else:
            given = ""
            given_parts = self.given.split("-")
            given = given_parts[0]
            for i in range(1, len(given_parts)):
                given += " -"+given_parts[i]

        given_parts = given.split(" ")

        given_abbrev = ""
        for given_part in given_parts:
            if given_part[0] == '-':
                given_abbrev = given_abbrev[:-1]
                given_abbrev += "-"+given_part[1] + ". "
            else:
                given_abbrev += given_part[0] + ". "
        given_abbrev = given_abbrev[:-1]
        return given_abbrev

    def fullfname( self ):
        return "{given} {family}".format(given=self.given, family=self.family)

    def fullname_abbrev( self):
        return "{given} {family}".format(given= self.given_abbrev(), family=self.family)


class manuscript :
    def __init__( self, doi ):
        try:
            cr_data = cr.works( ids = doi )
        except:
            print( "Failed CR Fetching w/ "+ doi)
            return 0
        self.doi = doi
        self.title = cr_data['message']['title'][0]
        self.journal = cr_data['message']['short-container-title'][0]

        try:
            authors_raw = cr_data['message']['author']
        except:
            print('No Author! You should skip')
            authors_raw = []

        try:
            self.volume = cr_data['message']['volume']
        except:
            self.volume = ""
        self.year = cr_data['message']['created']['date-parts'][0][0]

        try:
            self.number = cr_data['message']['page']
        except:
            try:
                self.number = cr_data['message']['article-number']
            except:
                self.number = ""
        

        self.authors = []
        for auth_raw in  authors_raw:
            given= auth_raw['given']
            family = auth_raw['family']
            self.authors.append( author( given, family ) )

    def cite_str( self ):
        cit = self.journal
        if len(self.volume) > 0 :
            cit += ", "+ self.volume

        if len(self.number) > 0 :
            if len(self.volume) > 0 :
                cit += ": "+ self.number
            else:
                cit += ", "+ self.number

        cit += "({year})".format(year=self.year)

        return cit

    def list_authors( self ):
        str = ""
        for author in self.authors:
            str += author.fullname_abbrev() + ", "
        return str[:-2]

    def full_info( self ):
        str = "'{title}' by\n{authors}\n{cite}\n{doi}".format(title=self.title, authors=self.list_authors(), cite=self.cite_str(), doi=self.doi)
        return str

    def cite( self ):
        if len( self.authors) == 1:
            author_str = self.authors[0].fullname_abbrev()
        elif len( self.authors) == 2:
            author_str = self.authors[0].fullname_abbrev() + " && " + self.authors[1].fullname_abbrev() 
        elif len( self.authors) == 3:
            author_str = self.authors[0].fullname_abbrev() + ", " +self.authors[1].fullname_abbrev() + " && " +self.authors[2].fullname_abbrev() 
        else :
            author_str = self.authors[0].fullname_abbrev() + " et al."

        return "{authors}, {cite}".format(authors=author_str, cite=self.cite_str())

    def journal_abbrev( self ):
        if self.journal == "Proceedings of the National Academy of Sciences":
            self.journal = "PNAS"
        elif self.journal == "Advances in Physics,":
            self.journal = "PNAS"

    def make_properties( self ) :
        prop =  {
            'properties': {
                'Authors': {
                    'rich_text' :[{
                        'text':{
                            'content':self.list_authors()
                        }
                    }]
                },
                'Citation': {
                    'rich_text' :[{
                        'text':{
                            'content':self.cite_str()
                        }
                    }]
                },
                'Title': {
                    'title' : [{
                        'text': {
                            'content':self.title
                        }
                    }]
                },
                'doi': {
                    'rich_text' :[{
                        'text':{
                            'content': self.doi,
                            'link': {'url':'https://doi.org/'+self.doi}
                        }
                    }]
                },
                'Managed':{
                    'checkbox': True
                }
            }
        }
        return prop