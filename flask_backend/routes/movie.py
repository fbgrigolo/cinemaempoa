import math

from flask import Blueprint, g, jsonify, render_template, request
from werkzeug.exceptions import abort

from flask_backend.repository.movies import get_all as get_all_movies
from flask_backend.repository.movies import (
    get_movies_with_similar_titles,
    get_paginated,
)
from flask_backend.routes.auth import login_required

bp = Blueprint("movie", __name__)


@bp.route("/movies")
def index():
    user_logged_in = g.user is not None
    movies = get_all_movies(user_logged_in)
    return render_template(
        "movie/index.html", movies=movies, show_drafts=user_logged_in
    )


@bp.route("/movies/posters")
def posters():
    page = request.args.get("page", 0)
    limit = request.args.get("limit", 12)
    try:
        page = int(page)
        limit = int(limit)
    except ValueError:
        abort(400)
    user_logged_in = g.user is not None
    movies = get_paginated(page, limit, user_logged_in)
    if len(movies) == 0:
        abort(404)

    imgDisplayWidth = 325
    images = []
    for movie in movies:
        for screening in movie.screenings:
            if screening.image:
                images.append(
                    {
                        "url": screening.image,
                        "width": imgDisplayWidth,
                        "height": math.ceil(
                            imgDisplayWidth
                            / screening.image_width
                            * screening.image_height
                        ),
                    }
                )

    return render_template(
        "movie/movies.html", images=images, show_drafts=user_logged_in, page=page
    )


@bp.route("/movies/search", methods=["GET"])
@login_required
def search_movies():
    title = request.args.get("title")
    movies = get_movies_with_similar_titles(title)
    return jsonify([{"title": movie.title} for movie in movies])
