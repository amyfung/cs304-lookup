'''
Flask/PyMySQL app to search the WMDb for people by name or movies by title.

Amy Fung
CS304
'''

from flask import (Flask, url_for, render_template,
                   request, flash, redirect)
import pymysql
import random
import queries
import os
import cs304dbi as dbi

app = Flask(__name__)

app.secret_key = ''.join([random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                         'abcdefghijklmnopqrstuvxyz' +
                                         '0123456789'))
                          for i in range(20)])


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    dbi.use('wmdb')
    print('will connect to {}'.format('wmdb'))


@app.route('/')
def index():
    """
    Renders the main page, containing the search form and a count of the current 
    number of people in the database.
    """
    conn = dbi.connect()

    (now, numPeople, numMovies) = queries.getNum(conn)

    # examples of database entries
    person = queries.selectRandomPerson(conn)
    movie = queries.selectRandomMovie(conn)

    # urls for examples
    personURL = url_for('showPerson', person_id_number=person['nm'])
    movieURL = url_for('showMovie', movie_id_number=movie['tt'])

    return render_template('base.html', now=now, numPeople=numPeople, 
                            numMovies=numMovies,person=person, 
                            personURL=personURL, movie=movie, movieURL=movieURL)


@app.route('/query/')
def query():
    """
    Processes the data received in the search form and determines what the user
    has searched for, what type of search the user has made, and what order the 
    user wants the results. 

    Searches for people or movies names or titles containing a fragment of the 
    searched term. 

    Redirects and informs user if no results are found. Returns redirect to the 
    matching page if one result is found. Returns template with a list of search 
    results linking to their respective pages if multiple results are found.
    """
    conn = dbi.connect()

    (now, numPeople, numMovies) = queries.getNum(conn)

    text = request.args.get('query')
    kind = request.args.get('kind')
    order = request.args.get('order')

    if kind == "person":
        results = queries.getPeople(conn, text, order)

        if len(results) == 0:
            flash("Sorry, no people were found with the search term '"
                  + text + "'")
            return render_template('notFound.html', kind="person", now=now,
                                   numPeople=numPeople, numMovies=numMovies)

        if len(results) == 1:
            return redirect(url_for('showPerson',
                                    person_id_number=results[0]["nm"]))

        results = queries.addURLs(conn, results, kind)

        return render_template('peopleList.html', length=len(results),
                               text=text, people=results, now=now,
                               numPeople=numPeople, numMovies=numMovies)

    elif kind == "movie":
        results = queries.getMovies(conn, text, order)

        if len(results) == 0:
            flash("Sorry, no movies were found for '" + text + "'")
            return render_template('notFound.html', kind="movie",
                                   now=now, numPeople=numPeople, 
                                   numMovies=numMovies)

        if len(results) == 1:
            return redirect(url_for('showMovie',
                                    movie_id_number=results[0]["tt"]))

        results = queries.addURLs(conn, results, kind)

        return render_template('movieList.html', length=len(results), text=text, 
                                results=results, now=now, numPeople=numPeople, 
                                numMovies=numMovies)


@app.route('/nm/<person_id_number>')
def showPerson(person_id_number):
    """
    Given the identification number of an actor or director, retrieves their 
    information from the person table and uses it to fill out the person's 
    detail page. Gathers the movies the person
    has worked on in the past. 

    If a person with the identification number is not found, reports and 
    redirects to a page that informs the user. Otherwise, renders the detail 
    page using the gathered information.
    """
    conn = dbi.connect()

    (now, numPeople, numMovies) = queries.getNum(conn)

    person = queries.getPerson(conn, person_id_number)

    if not person:
        flash("Sorry, no person with that ID is in the database")
        return render_template('notFound.html', kind="person", now=now,
                               numPeople=numPeople, numMovies=numMovies)

    addedby = queries.getStaff(conn, person['addedby'])
    movies = queries.addURLs(conn, queries.getPastMovies(conn, 
                            person_id_number), "movie")

    return render_template('personDetails.html', movies=movies, person=person,
                           addedby=addedby, now=now, numPeople=numPeople,
                           numMovies=numMovies)


@app.route('/tt/<movie_id_number>')
def showMovie(movie_id_number):
    """
    Given a movie identification number, retrieves information about the 
    corresponding movie. If identification number not found in WMDb, reports so 
    and renders an error page. Otherwise renders the movie detail page.  
    """
    conn = dbi.connect()

    (now, numPeople, numMovies) = queries.getNum(conn)

    movie = queries.getMovie(conn, movie_id_number)

    if not movie:
        flash("Sorry, no movie with that ID is in the database")
        return render_template('notFound.html', kind="movie", now=now, 
                                numPeople=numPeople, numMovies=numMovies)

    addedby = queries.getStaff(conn, movie['addedby'])
    director = queries.getDirector(conn, movie['director'])
    cast = queries.addURLs(conn, queries.getCast(
        conn, movie_id_number), "person")

    return render_template('movieDetails.html', cast=cast, movie=movie, 
                            director=director, addedby=addedby, now=now, 
                            numPeople=numPeople, numMovies=numMovies)


if __name__ == '__main__':
    import sys
    import os
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        assert (port > 1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0', port)
