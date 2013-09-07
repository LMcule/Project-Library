# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
##auth.define_tables(username=False, signature=False)
auth.next = None
auth.settings.login_next = URL('profile') 
auth.settings.profile_next = URL('profile')

## configure email
from gluon.tools import Mail
mail=Mail()
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'shikher111@gmail.com'
mail.settings.login = 'projectlibraryiiit:sister1182'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

import datetime

db.define_table(
	auth.settings.table_user_name,
	Field('first_name', length=128, default=''),
	Field('last_name', length=128, default=''),
	Field('email', length=128, default='', unique=True),
	Field('password', 'password', length=512,
		readable=False, label='Password'),
	Field('profile_pic',type='upload',default=None,readable=False),
	Field('registration_date', 'date',
		writable=False, readable=False, default=datetime.date.today()),
	Field('registration_key', length=512,
		writable=False, readable=False, default=''),
	Field('reset_password_key', length=512,
		writable=False, readable=False, default=''),
	Field('registration_id', length=512,
		writable=False, readable=False, default=''),
	Field('upload_count',type='integer', writable=False, readable=False, default='0'),
	Field('country',type='string')
	)
custom_auth_table = db[auth.settings.table_user_name] 
custom_auth_table.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email),IS_NOT_IN_DB(db, custom_auth_table.email)]
auth.settings.table_user = custom_auth_table
auth.define_tables()
auth.settings.table_user_name ='auth_user'	


db.define_table('project',
	Field('project_name',type='string',length=13,unique=True),
	Field('project_pic',type='upload',default=None),
	Field('description',type='text'),
	Field('projectadmin_email',writable=False,readable=False,default=None),
## add versions
	Field('type_of_project',requires=IS_IN_SET(['Course','Thesis','Research Paper','MSIT','Other'])),
	Field('category',requires=IS_IN_SET(['Audio & Video','Business & Enterprise','Communications','Development','Home & Education','Games','Graphics','Science & Engineering','Websites','Others'])),
	Field('project_admin_year',requires=IS_IN_SET(['BTECH','MS','MTECH','PHD'])),
	Field('num_comments',type='integer',default='0',readable=False,writable=False ),
	Field('date_added',type='date',default=datetime.date.today(),readable=False,writable=False),
	Field('num_downloads',type='integer',default='0',readable=False,writable=False ),
	Field('num_rating',type='integer',default='0',readable=False,writable=False ),
	Field('total_rating',type='integer',default='0',readable=False,writable=False ),
	Field('avg_rating',type='float',default='0',readable=False,writable=False)
	)

db.define_table('allowed_users',
		Field('projectadmin_email',type='string'),
		Field('other_email',type='string'),
		Field('project_name',type='string')
		)

db.define_table('files',
		Field('file_name',type='string',default=None),
		Field('project_file',type='upload',default=None),
		Field('file_description',type='text'),
		Field('project_version',type='integer',default=0,writable=False,readable=False),
		Field('project_id','reference project',writable=False, readable=False))
db.define_table('flak',
		Field('user_id','integer'),
		Field('project_id','integer'),
		Field('all_flag','boolean',default=False),
		Field('comments_flag','boolean',default=False),
		Field('download_flag','boolean',default=False),
		Field('rating_flag','boolean',default=False),
		)

db.files.project_id.requires = IS_IN_DB(db, db.project.id, '%(project_name)s')


db.define_table('subscribe',
		Field('cur_user',type='string',default=None),
		Field('sub_user','reference auth_user',default=None),
		Field('is_sub',type='boolean'))
db.subscribe.sub_user.requires = IS_IN_DB(db, db.auth_user.id, '%(email)s')

#db.define_table('uploaded_projects',
#	Field('project_id','reference project',writable=False,readable=False,default='0'),
#	Field('uploader','reference auth_user',writable=False,readable=False,default='0')
#	)
#db.uploaded_projects.project_id.requires = IS_IN_DB(db, db.project.id, '%(project_name)s')
#db.uploaded_projects.uploader.requires = IS_IN_DB(db, db.auth_user.id, '%(email)s')

db.define_table('kolect',
		Field('cur_user',type='string',default=None),
		Field('project_id','reference project',default=None),
		Field('is_sub',type='boolean'))
db.kolect.project_id.requires = IS_IN_DB(db, db.project.id, '%(project_name)s')


db.define_table('comments',
		Field('comment_c',type='text'),
		Field('commenter_c',type='string',readable=False,writable=False),
		Field('project_id','reference project',writable=False, readable=False))


db.comments.project_id.requires = IS_IN_DB(db, db.project.id, '%(project_name)s')


