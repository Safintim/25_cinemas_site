import requests
from bs4 import BeautifulSoup


def get_movies_today_in_cinemas(city, count=10):
    url_afisha = 'https://www.afisha.ru/{}/schedule_cinema/'.format(city)
    afisha_page = fetch_afisha_page(url_afisha)
    movies = get_movies_from_afisha_page(afisha_page, count)

    for movie in movies:
        movie_afisha_page = fetch_movie_page(movie['movieUrl'])
        movie.update(get_additional_info_movie(movie_afisha_page))
        kinopoisk_search_page = fetch_search_page_by_title(movie['title'])
        movie_id = get_movie_id_from_search_page(kinopoisk_search_page)
        xml_rating = fetch_movie_info_xml(movie_id)
        rating_movie = get_rating_movie_from_xml(xml_rating)
        movie.update(rating_movie)
        yield movie


def sorted_movies_by_rating(movies):
    return sorted(movies, key=lambda movie: movie['rating'], reverse=True)


def fetch_afisha_page(url_afisha):
    response = requests.get(url_afisha)
    response.raise_for_status()
    return response.text


def get_movies_from_afisha_page(raw_html, count=10):
    soup = BeautifulSoup(raw_html, 'html.parser')
    movies = []
    for li in soup.select('#widget-content ul li')[:count]:
        movies.append({
            'title': li.select_one('h3 a').text,
            'movieUrl': 'https://www.afisha.ru{}'.format(li.select_one('div.imageWrapper___25LKp a').attrs['href']),
            'imageUrl': li.select_one('div.seo meta[itemprop="image"]').attrs['content'],
            'shortDescription': li.select_one('h3').find_next_sibling('div').text,
            'director': li.select_one('div.seo div[itemprop="director"] meta').attrs['content'],
        })

    return movies


def fetch_movie_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def get_additional_info_movie(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    info_widget = soup.select_one('div.info-widget')
    genres = [genre.text for genre in info_widget.select('ul li.info-widget__meta-item_genres a span')]
    return {
        'countHours': info_widget.select_one('ul li.info-widget__meta-item span meta').parent.text,
        'genre': ', '.join(genres),
        'description': info_widget.select_one('p.info-widget__description').text,
    }


def fetch_search_page_by_title(movie_title):
    url = 'http://www.kinopoisk.ru/index.php'
    params = {
        'kp_query': movie_title
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text


def get_movie_id_from_search_page(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.select_one('div.most_wanted p.name a').attrs['data-id']


def fetch_movie_info_xml(movie_id):
    url = 'https://rating.kinopoisk.ru/{}.xml'.format(movie_id)
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def get_rating_movie_from_xml(xml):
    soup = BeautifulSoup(xml, 'lxml')
    imdb_rating = soup.find('imdb_rating')
    rating_info = {
        'votes': 0,
        'rating': 0
    }
    if imdb_rating:
        rating_info['votes'] = int(imdb_rating.attrs['num_vote'])
        rating_info['rating'] = float(imdb_rating.get_text())

    return rating_info
