import os
from flask import Flask,jsonify,request,abort
from functools import wraps
from urlparse import urlparse
from newspaper import Article
from pyembed.core import PyEmbed

app = Flask(__name__)

def check_auth(username,password):
    return username == 'meet' and password == 'secret'

def authenticate():
    message = {'message' : 'Authenticate'}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="ExtractAPI"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()

        elif not check_auth(auth.username,auth.password):
            return authenticate()
        return f(*args,**kwargs)
    return decorated


@app.route('/')
def api_root():
    return "Hello World"

@app.route('/article')
@requires_auth
def api_article():
    if 'url' in request.args:
        url_string = urlparse(request.args['url'])
        hostname = url_string.hostname
        checkImages = url_string.path.endswith(('.png','.jpeg','.gif','.webp','.svg','.jpg'))
        article = Article(request.args['url'],keep_article_html = True)
        if hostname in ['vimeo.com','youtube.com','dailymotion.com','hulu.com','www.youtube.com','www.vimeo.com','www.dailymotion.com','www.hulu.com']:
            video_src = PyEmbed().embed(request.args['url'])
        else:
            video_src = ""

        article.download()
        if article.html == "":
            abort(404)
        else:
            article.parse()

        data = {
            'url' : article.url,
            'title' : article.title,
            'image': request.args['url'] if checkImages else article.top_img,
            'images' : [x for x in article.imgs],
            'text' : article.text,
            'html' : article.article_html,
            'authors': article.authors,
            'summary': article.meta_description,
            'meta_lang': article.meta_lang,
            'meta_favicon': article.meta_favicon,
            'meta_keywords': article.meta_keywords,
            'canonical_link': article.canonical_link,
            'tags' : [unicode(x) for x in article.tags],
            'additional_data': article.additional_data,
            'video' : video_src if not False else ""
        }

        resp = jsonify(data)
        resp.status_code = 200
        return resp

    else:
        abort(400)

if __name__ == '__main__':
    app.run(debug=True)