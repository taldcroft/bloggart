import sys
sys.path.append('lib')
import models
import static
import asciitable
import re
import google.appengine.ext.bulkload.transform as transform

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

# ccosmos% remote_api_shell.py --server=localhost:8080 py4ast20
# Email: asdf
# Password: 
# App Engine remote_api shell
# Python 2.6.3 (r263:75183, Oct 29 2009, 10:05:51) 
# [GCC 4.1.2 20080704 (Red Hat 4.1.2-46)]
# The db, users, urlfetch, and memcache modules are imported.
# py4ast20> import my_migrate
# Traceback (most recent call last):
#   File "<console>", line 1, in <module>
# ImportError: No module named my_migrate
# py4ast20> import sys
# py4ast20> sys.path.append('.')
# py4ast20> import my_migrate
# py4ast20> my_migrate.migrate_all()


datetransform = transform.import_date_time('%Y-%m-%dT%H:%M:%S')
lexer = get_lexer_by_name("python", stripall=True)
formatter = HtmlFormatter(style='colorful')
code_block = re.compile(r'<pre name="code" class="python">(.*?)</pre>')

def highlight(code_match):
    code = code_match.group(1)
    code = re.sub(r'<br />', '\n', code)
    return pygments.highlight(code, lexer, formatter)

def migrate_one(article, path, dry_run=False):
    # logging.debug("Migrating post with key %s", post_key)
    article_html = code_block.sub(highlight, unicode(article['body'], encoding='utf-8'))
    kwargs = dict(path=path,
                  title=unicode(article['title'], encoding='utf-8'),
                  body=article_html,
                  tags=set(eval(article['tags'] or '[]')),
                  published=datetransform(article['published']),
                  updated=datetransform(article['updated']),
                  deps={})
    try:
        print 'Looking for path', path
        keys = models.BlogPost.all(keys_only=True).filter('path =', path)
        kwargs['key'] = keys[0]
        print 'Reusing existing post key', key
    except:
        print 'Making new post'
        
    post = models.BlogPost(**kwargs)
    print article['published'], post.published
    if not dry_run:
        post.put()

def migrate_all(num=2, dry_run=False):
##        for sc in static.StaticContent.all():
##            sc.delete()
##        for post in models.BlogPost.all():
##            post.delete()

    articles = asciitable.read('articles.csv', delimiter=',', quotechar='"')
    for article in articles[slice(0, num)]:
        path = re.sub(r'^[a-z]+', '', article['permalink'])
        if not path.startswith('/'):
            path = '/' + path
        print article['key'], article['title'], path
        migrate_one(article, path, dry_run)
