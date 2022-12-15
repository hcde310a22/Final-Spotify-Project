from flask import Flask, request, redirect, render_template
import urllib
import json
import requests
from datetime import datetime
from wtforms import Form, StringField, SelectField, validators, SubmitField, IntegerField


def get_spotify_token():
    token_url = 'https://accounts.spotify.com/api/token'
    # data = {'client_credentials':''}
    clientId = '81ea18661eda4b758e99424bb7c4439c'
    clientSecret = '677c14c9912c47069011bd2f5d052923'
    # Working code for access token
    request_body = {
        "grant_type": 'client_credentials',
        "response_type": 'code',
        "redirect_uri": 'http://localhost:8888/',
        "client_id": f"{clientId}",
        "client_secret": f"{clientSecret}",
    }
    r = requests.post(url=token_url, data=request_body)
    resp = r.json()
    print(resp)
    token = resp['access_token']
    token_type = resp['token_type']
    return token, token_type


def search_spotify(token, token_type, artist, year, genre):
    qdata = urllib.parse.urlencode({'artist': artist, 'year': year, 'genre': genre})
    # data = {'artist':'Drake', 'year':2001}
    # Working code for search endpoint
    searchUrl = 'https://api.spotify.com/v1/search'
    search_resp = requests.get(
        searchUrl,
        headers={'Authorization': f"{token_type} {token}"},
        params={'q': qdata, 'type': 'artist'})
    artist_info = search_resp.json()

    urls = []
    for item in artist_info['artists']['items']:
        urls.append(f"<a href={item['external_urls']['spotify']}>{item['name']} Popularity: {item['popularity']}</a><br>")
    return " ".join(urls)


class SpotifyAccess(Form):
    artistname = StringField('artist name', [validators.Length(min=2, max=25)])
    year = IntegerField('year', [validators.NumberRange(min=1980, max=2022)])
    genre_list = ('Hip Hop','Pop','Rock','Rhythm and Blues','Jazz','Classical','Dance','Soul','Disco','Rap','Blues','Drill','k-pop')
    genre = SelectField(label = 'genre', choices = genre_list, validate_choice=False)
    submit = SubmitField('submit')


form = None
app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def home():
    form = SpotifyAccess(request.form)
    if form.validate():
        artist = form.artistname.data
        year = form.year.data,
        genre = form.genre.data
        token, token_type = get_spotify_token()
        urls = search_spotify(token, token_type, artist, year, genre)
        return f'<p>{urls}</p>'
    return render_template('index.html',
                           title='Search Spotify Artists',
                           form=form)

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)