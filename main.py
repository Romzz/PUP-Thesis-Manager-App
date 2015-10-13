import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users
import jinja2
import os
import logging
import json
import csv
import cgi

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Faculty(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)

    @classmethod
    def get_by_key(cls, keyname):
        try:
            return ndb.Key(cls, keyname).get()
        except Exception:
            return None

class ThesisDB(ndb.Model):
    year = ndb.StringProperty(indexed=True)
    title = ndb.StringProperty(indexed=True)
    subtitle = ndb.StringProperty(indexed=True)
    abstract = ndb.TextProperty()
    section = ndb.StringProperty(indexed=True)
    adviser_key = ndb.KeyProperty(indexed=True,kind=Faculty)
    proponent_keys = ndb.KeyProperty(repeated=True)
    department_key = ndb.KeyProperty(indexed=True)
    tags = ndb.StringProperty(repeated=True)
    member1 = ndb.StringProperty(indexed=True)
    member2 = ndb.StringProperty(indexed=True)
    member3 = ndb.StringProperty(indexed=True)
    member4 = ndb.StringProperty(indexed=True)
    member5 = ndb.StringProperty(indexed=True)

    created_by = ndb.KeyProperty(indexed=True)
    created_date = ndb.DateTimeProperty(auto_now_add=True)

class Student(ndb.Model):
    first_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)

class Department(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    college_key = ndb.KeyProperty(indexed=True)

    @classmethod
    def get_by_key(cls, id):
        try:
            return ndb.Key(cls, id).get()
        except Exception:
            return None

class College(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    university_key = ndb.KeyProperty(indexed=True)

class University(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    initials = ndb.StringProperty(indexed=True)

class User(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    created_date = ndb.DateTimeProperty(auto_now_add=True)

class ImportHandler(webapp2.RequestHandler):
    def get(self):
        file = open(os.path.join(os.path.dirname(__file__), 'PUP COE Thesis List.csv'))
        fileReader = csv.reader(file)

        department_key = ndb.Key(urlsafe='ah5kZXZ-cHVwLWRibXMtdGhlc2lzLW1hbmFnZXItMTlyFwsSCkRlcGFydG1lbnQiB0NPRV9QVVAM')
        department = department_key.get()
        college = department.college_key.get()
        university = college.university_key.get()
        logging.info(department.name + ' ' + college.name + ' ' + university.initials)


        for row in fileReader:
            thesis = ThesisDB()
            thesis.year = row[3]
            thesis.title = row[4]
            subtitle = ''
            thesis.abstract = row[5]
            thesis.section = row[6]
            thesis.department_key = department_key
            thesis.tags = ['pupcoe', 'mcu']
            adviser_name = row[7]
            adviser_keyname = adviser_name.strip().replace(' ', '').lower()
            adviser = Faculty.get_by_key(adviser_keyname)

            if adviser is None:
                adviser = Faculty(key=ndb.Key(Faculty, adviser_keyname), name=adviser_name)
                adviser.put()
            thesis.adviser_key = adviser.key
            thesis.member1 = row[8]
            thesis.member2 = row[9]
            thesis.member3 = row[10]
            thesis.member4 = row[11]
            thesis.put()

        self.redirect('/')

class SetupDBHandler(webapp2.RequestHandler):
    def get(self):

        university = University(name='Polytechnic University of the Philippines', initials='PUP')
        university.put()

        up = University(name='University of the Philippines', initials='UP')
        up.put()

        college = College(name='Engineering', university_key=university.key)
        college.put()

        college_up = College(name='Engineering', university_key=up.key)
        college_up.put()

        archi_college = College(name='Architecture', university_key=university.key)
        archi_college.put()

        coe_department = Department(name='COE', college_key=college.key, id='COE_PUP')
        coe_department.put()

        coe_up_department = Department(name='COE', college_key=college_up.key, id='COE_UP')
        coe_up_department.put()

        cafa_department = Department(name='CAFA', college_key=archi_college.key, id='CAFA_PUP')
        cafa_department.put()

        self.response.write('Datastore setup completed')

class LoginPageHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_env.get_template('login.html')
        self.response.write(template.render())

class RegisterPageHandler(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()

        if loggedin_user:
            user_key = ndb.Key('User', loggedin_user.user_id())
            user = user_key.get()
            if user:
                self.redirect('/home')
            else:
                template = jinja_env.get_template('register.html')
                logout_url = users.create_logout_url('/register')
                template_values = {
                    'logout_url': logout_url
                }
                self.response.write(template.render(template_values))
        else:
            login_url = users.create_login_url('/register')
            self.redirect(login_url)

    def post(self):
        loggedin_user = users.get_current_user()
        user = User(id=loggedin_user.user_id(), email=loggedin_user.email(),
                     first_name=self.request.get('first_name'),
                     last_name=self.request.get('last_name'))
        user.put()
        self.redirect('/home')

class ThesisListAll(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url('/login')
        url_linktext = 'Logout'


        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = jinja_env.get_template('thesis-all.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect(users.create_login_url('/login'))

class APIThesis(webapp2.RequestHandler):
    def get(self):
        thesis = ThesisDB.query().order(-ThesisDB.year).fetch()
        thesis_list = []

        for paper in thesis:
            adviser_url = paper.adviser_key.urlsafe()
            adviser_key = ndb.Key(urlsafe=adviser_url)
            advs_key = adviser_key.get()
            adviser = advs_key.name
            thesis_list.append({
                'year': paper.year,
                'title': paper.title,
                'abstract': paper.abstract,
                'adviser' : adviser,
                'section' : paper.section,
                'member1' : paper.member1,
                'member2' : paper.member2,
                'member3' : paper.member3,
                'member4' : paper.member4,
                'member5' : paper.member5
            })

        response = {
            'result': 'OK',
            'data': thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class ThesisFilterHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url('/login')
        url_linktext = 'Logout'


        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = jinja_env.get_template('thesis-filter.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect(users.create_login_url('/login'))
    def post(self):
        selected = self.request.get('selection')
        api_url = '/api/thesis/'+selected
        user = users.get_current_user()
        url = users.create_logout_url('/login')
        url_linktext = 'Logout'

        template_data = {
            'selected' : selected,
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        template = jinja_env.get_template('thesis-filter.html')
        self.response.write(template.render(template_data))

class APIThesisFilterAll(webapp2.RequestHandler):
    def get(self):
        thesis = ThesisDB.query().order(-ThesisDB.year).fetch()
        thesis_list = []

        for paper in thesis:
            adviser_url = paper.adviser_key.urlsafe()
            adviser_key = ndb.Key(urlsafe=adviser_url)
            advs_key = adviser_key.get()
            adviser = advs_key.name
            thesis_list.append({
                'year': paper.year,
                'title': paper.title
            })

        response = {
            'result': 'OK',
            'data': thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class APIThesisFilterByYear2011(webapp2.RequestHandler):
    def get(self):
        thesis = ThesisDB.query(ThesisDB.year == '2011').order(-ThesisDB.year).fetch()
        thesis_list = []

        for paper in thesis:
            thesis_list.append({
                'year': paper.year,
                'title': paper.title,
                'abstract': paper.abstract,
                # 'adviser' : paper.adviser,
                'section' : paper.section
            })

        response = {
            'result': 'OK',
            'data': thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class APIThesisFilterByYear2012(webapp2.RequestHandler):
    def get(self):
        thesis = ThesisDB.query(ThesisDB.year == '2012').order(-ThesisDB.year).fetch()
        thesis_list = []

        for paper in thesis:
            thesis_list.append({
                'year': paper.year,
                'title': paper.title,
                'abstract': paper.abstract,
                # 'adviser' : paper.adviser,
                'section' : paper.section
            })

        response = {
            'result': 'OK',
            'data': thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class APIThesisFilterByYear2013(webapp2.RequestHandler):
    def get(self):
        thesis = ThesisDB.query(ThesisDB.year == '2013').order(-ThesisDB.year).fetch()
        thesis_list = []

        for paper in thesis:
            thesis_list.append({
                'year': paper.year,
                'title': paper.title,
                'abstract': paper.abstract,
                # 'adviser' : paper.adviser,
                'section' : paper.section
            })

        response = {
            'result': 'OK',
            'data': thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class APIThesisFilterByYear2014(webapp2.RequestHandler):
    def get(self):
        thesis = ThesisDB.query(ThesisDB.year == '2014').order(-ThesisDB.year).fetch()
        thesis_list = []

        for paper in thesis:
            thesis_list.append({
                'year': paper.year,
                'title': paper.title,
                'abstract': paper.abstract,
                # 'adviser' : paper.adviser,
                'section' : paper.section
            })

        response = {
            'result': 'OK',
            'data': thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class APIThesisFilterByYear2015(webapp2.RequestHandler):
    def get(self):
        thesis = ThesisDB.query(ThesisDB.year == '2015').order(-ThesisDB.year).fetch()
        thesis_list = []

        for paper in thesis:
            thesis_list.append({
                'year': paper.year,
                'title': paper.title,
                'abstract': paper.abstract,
                # 'adviser' : paper.adviser,
                'section' : paper.section
            })

        response = {
            'result': 'OK',
            'data': thesis_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url('/login')
        url_linktext = 'Logout'
        deps = Department()

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'deps' : deps
        }
        if user:
            template = jinja_env.get_template('index.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect(users.create_login_url('/login'))

class ThesisUploadHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url('/login')
        url_linktext = 'Logout'

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = jinja_env.get_template('thesis-create.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect(users.create_login_url('/login'))

    def post(self):

        loggedin_user = users.get_current_user()
        thesis = ThesisDB()
        thesis.year = self.request.get('thesis_year')
        thesis.title = self.request.get('thesis_title')
        thesis.subtitle = self.request.get('thesis_subtitle')
        thesis.abstract = self.request.get('thesis_abstract')
        thesis.section = self.request.get('thesis_section')
        selected = self.request.get('thesis_department')
        # logging.info(selected)
        something = ndb.Key(Department,selected)
        # logging.info(something)
        something_key = something.urlsafe()
        # logging.info(something_key)
        deps_key = ndb.Key(urlsafe=something_key)
        # logging.info(deps_key)
        thesis.department_key = deps_key
        thesis.tags = ['pupcoe', 'mcu']
        adviser_name = self.request.get('thesis_adviser')
        adviser_keyname = adviser_name.strip().replace(' ', '').lower()
        adviser = Faculty.get_by_key(adviser_keyname)
        if adviser is None:
            adviser = Faculty(key=ndb.Key(Faculty, adviser_keyname), name=adviser_name)
            adviser.put()
        thesis.adviser_key = adviser.key
        thesis.member1 = self.request.get('thesis_member1')
        thesis.member2 = self.request.get('thesis_member2')
        thesis.member3 = self.request.get('thesis_member3')
        thesis.member4 = self.request.get('thesis_member4')
        thesis.member5 = self.request.get('thesis_member5')
        user_key = ndb.Key('User', loggedin_user.user_id())
        user_urlsafe = user_key.urlsafe()
        user = ndb.Key(urlsafe=user_urlsafe)
        thesis.created_by = user
        thesis.put()

        self.redirect('/home')

class APITFacultyList(webapp2.RequestHandler):
    def get(self):
        faculty = Faculty.query().order(-Faculty.name).fetch()
        faculty_list = []

        for someone in faculty:
            faculty_list.append({
                'name' : someone.name
                })

        response = {
            'result' : 'OK',
            'data' : faculty_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

class APIDepartmentList(webapp2.RequestHandler):
    def get(self):
        department_list = []
        department = Department.query().order(-Department.college_key).fetch()

        for someone in department:
            qry = Department.query(Department.college_key==someone.college_key).get()
            department_id = qry.key.id()

            college_key = someone.college_key
            college = college_key.get()
            university = college.university_key.get()

            department_list.append({
                'name' : someone.name,
                'college' : college.name,
                'university' : university.initials,
                'id' : department_id
                })

        response = {
            'result' : 'OK',
            'data' : department_list
        }

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

app = webapp2.WSGIApplication([
    ('/', LoginPageHandler),
    ('/home', MainPage),
    ('/thesis/create', ThesisUploadHandler),
    ('/thesis/list/all', ThesisListAll),
    ('/login', LoginPageHandler),
    ('/register', RegisterPageHandler),
    ('/filter', ThesisFilterHandler),
    ('/setup', SetupDBHandler),
    ('/importcsv', ImportHandler),
    ('/api/thesis', APIThesis),
    ('/api/thesis/faculty', APITFacultyList),
    ('/api/thesis/department', APIDepartmentList),
    ('/api/thesis/all', APIThesisFilterAll),
    ('/api/thesis/2011', APIThesisFilterByYear2011),
    ('/api/thesis/2012', APIThesisFilterByYear2012),
    ('/api/thesis/2013', APIThesisFilterByYear2013),
    ('/api/thesis/2014', APIThesisFilterByYear2014),
    ('/api/thesis/2015', APIThesisFilterByYear2015),
], debug=True)