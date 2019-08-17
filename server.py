import tempfile
from flask import Flask, render_template
from werkzeug.contrib.cache import FileSystemCache
from cinemas import get_movies_today_in_cinemas, sorted_movies_by_rating

app = Flask(__name__)
tmp_dir = tempfile.mkdtemp()
cache = FileSystemCache(cache_dir=tmp_dir, default_timeout=60*60*3)


@app.route('/')
def films_list():
    films_list = cache.get('films_list')
    if films_list:
        return films_list
    else:
        movies = sorted_movies_by_rating(get_movies_today_in_cinemas(city='kazan'))
        response = render_template('films_list.html', grouped_movies=group_items_in_array(movies))
        cache.set('films_list', response)
        return response


def group_items_in_array(array, group_volume=2):
    grouped_items = []
    for start_index_group in range(0, len(array), group_volume):
        grouped_items.append(array[start_index_group:start_index_group+group_volume])
    return grouped_items


if __name__ == '__main__':
    app.run()
