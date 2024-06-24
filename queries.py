from flask import (Flask, url_for, render_template,
                   request, flash, redirect)
import cs304dbi as dbi
import app
import sys
from datetime import datetime

# ==========================================================
# Helper functions that perform queries


def addURLs(conn, results, kind):
    """
    Helper function that is given search results in the form of a list of 
    dictionaries, as well as the type of search that has been made, in order to
    add the URL for every person or movie in the results to their corresponding 
    dictionary. Returns this modified dictionary.
    """
    curs = dbi.dict_cursor(conn)

    if kind == "person":
        for person in results:
            person['url'] = url_for(
                'showPerson', person_id_number=person['nm'])
    else:
        for movie in results:
            movie['url'] = url_for('showMovie', movie_id_number=movie['tt'])
    return results


def getAllPeople(conn):
    """
    Returns all people in WMDb.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select distinct nm, name, birthdate from person''')
    return curs.fetchall()


def getAllMovies(conn):
    """
    Returns all movies in WMDb.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from movie')
    return curs.fetchall()


def getNum(conn):
    """
    Returns the current date and time, as well as the number of people and 
    number of movies in WMDb.
    """
    curs = dbi.dict_cursor(conn)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    numPeople = len(getAllPeople(conn))
    numMovies = len(getAllMovies(conn))
    return (now, numPeople, numMovies)


def selectRandomPerson(conn):
    """
    Returns nm, nate, and birthdate from a randomly selected person.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                select nm, name, birthdate 
                from person 
                order by rand() 
                limit 1''')
    return curs.fetchone()


def selectRandomMovie(conn):
    """
    Returns tt, title, and release data from a randomly selected movie.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select tt, title, `release` 
                from movie order by rand() limit 1''')
    return curs.fetchone()


def getPerson(conn, nm):
    """
    Given an nm, returns the corresponding row from the WMDb person table.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from person where nm = %s''', [nm])
    person = curs.fetchone()
    return person


def getStaff(conn, uid):
    """
    Given an uid, returns the corresponding name from the WMDb staff table
    or N/A if the uid is NoneType.
    """
    curs = dbi.dict_cursor(conn)
    if uid:
        curs.execute('''
                    select name from staff
                    where uid = %s''',
                    [uid])
        return curs.fetchone()['name']
    else:
        return "N/A"


def getDirector(conn, nm):
    """
    Given an nm value, returns the corresponding director from the WMDb credit 
    table. Returns "N/A" if the nm is NoneType.
    """
    curs = dbi.dict_cursor(conn)
    if nm:
        curs.execute('''
                    select * from person
                    where nm = %s''',
                    [nm])
        return curs.fetchone()
    else:
        return "N/A"


def getMovie(conn, tt):
    """
    Given a tt value, returns the corresponding movie from the WMDb movie table.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from movie where tt = %s''', [tt])
    movie = curs.fetchone()
    return movie


def getPeople(conn, text, order):
    """
    Given a search term, returns a list of dictionaries representing the people 
    in the WMDb whose names contain the term.
    """
    curs = dbi.dict_cursor(conn)
    if order == "name":
        curs.execute('''
                    select name, birthdate, nm 
                    from person 
                    where name like %s 
                    order by LTRIM(name)''', 
                    ["%"+text+"%"])
    elif order == "oldest to youngest":
        curs.execute('''
                    select name, birthdate, nm 
                    from person 
                    where name like %s 
                    order by birthdate''', [
                     "%"+text+"%"])
    elif order == "youngest to oldest":
        curs.execute('''
                    select name, birthdate, nm 
                    from person 
                    where name like %s 
                    order by birthdate desc''', [
                     "%"+text+"%"])
    else:
        curs.execute('''
                    select name, birthdate, nm 
                    from person 
                    where name like %s''', [
                     "%"+text+"%"])
    return curs.fetchall()


def getMovies(conn, text, order):
    """
    Given a search term, returns a list of dictionaries representing the movies 
    in the WMDb database whose titles contain the search string.
    """
    curs = dbi.dict_cursor(conn)
    if order == "release year (oldest first)":
        curs.execute('''
                    select * from movie where title like %s 
                    order by cast(`release` as int)''', 
                    ["%"+text+"%"])
    elif order == "release year (newest first)":
        curs.execute('''
                    select * from movie where title like %s 
                    order by cast(`release` as int) desc''', 
                    ["%"+text+"%"])
    else:  
        curs.execute('''
                    select * from movie where title like %s order by title''', 
                    ["%"+text+"%"])
    return curs.fetchall()


def getCast(conn, tt):
    """
    Given a movie's identification number, returns a list of dictionaries that 
    representthe people who are credited for working on it and who are in the 
    WMDb.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                select nm, name, birthdate 
                from person 
                where person.nm in 
                    (select distinct nm 
                    from credit 
                    where credit.tt = %s)''', 
                [tt])
    return curs.fetchall()


def getPastMovies(conn, nm):
    """
    Given a person's identification number, returns a list of dictionaries that 
    represent the movies they are credited for in the WMDb.
    """
    curs = dbi.dict_cursor(conn)
    curs.execute(
        '''select * 
        from movie 
        where movie.tt in 
            (select distinct tt 
            from credit 
            where credit.nm = %s)''', 
        [nm])
    return curs.fetchall()
