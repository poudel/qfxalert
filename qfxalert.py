import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from texttable import Texttable
from qfx import QFXScraper
from simple_config import Config


config = Config(
    os.path.join(os.environ["HOME"], "qfxalert.json"),
    defaults={
        "movies": [],
        "subscribed_keywords": ["avengers", "infinity", "3d"],
        "subscribers": ["self@example.com"],
        "from_mail": "hmm@hmm.com",
        "mail_user": None,
        "mail_password": None,
        "mail_host": "localhost",
        "mail_port": 1025,
        "mail_ssl": False
    }
)


def serialize_movie(movie):
    fields = ['event_id', 'tickets', 'title']
    return {k: getattr(movie, k) for k in fields}


def is_subscribed(title):
    yes = False
    title_list = title.lower().split(" ")

    for keyword in config.subscribed_keywords:
        if keyword.lower() in title_list:
            yes = True
            break
    return yes


def alert_when_delta():
    scraper = QFXScraper()

    pulled = {}

    # let's make a list of only relevant movies
    for m in scraper.get_movies():
        if is_subscribed(m.title):
            movie = serialize_movie(m)
            pulled[movie['event_id']] = movie

    fresh = []
    expired = []

    old = {}

    for movie in config.movies:
        if movie['event_id'] in pulled.keys():
            old[movie['event_id']] = movie
        else:
            if is_subscribed(movie['title']):
                # sometimes expired movies may have been unsubbed
                expired.append(movie)

    movies = []
    for event_id, new_version in pulled.items():
        old_version = old.get(event_id)

        movies.append(new_version)

        if old_version:
            if old_version['tickets'] != new_version['tickets']:
                print("Tickets update for: {}".format(new_version['title']))
                fresh.append(new_version)
        else:
            print("New one found: {}".format(new_version['title']))
            fresh.append(new_version)

    if not fresh:
        return

    config.update(movies=movies)

    printables = []

    for m in movies:
        if m['tickets']:
            m['tickets'] = "https://qfxcinemas.com{tickets}".format(**m)

        printable = (
            "------------------------------------------------\n"
            "Title: {title}\n"
            "Tickets: {tickets}\n"
            "------------------------------------------------\n"
            .format(**m)
        )
        printables.append(printable)


    email_message = """
Yo!!

There's some update in the movie keywords you've subscribed:

{}

""".format("\n".join(printables))

    message = MIMEMultipart()
    message['Subject'] = 'Movie ticket updates'
    message['From'] = config.from_mail
    message['To'] = ', '.join(config.subscribers)
    message.attach(MIMEText(email_message))

    try:
        if config.mail_ssl:
            server = smtplib.SMTP_SSL(config.mail_host, config.mail_port)
        else:
            server = smtplib.SMTP(config.mail_host, config.mail_port)

        server.ehlo()

        if config.mail_password:
            server.login(config.mail_user, config.mail_password)

        server.sendmail(config.from_mail, config.subscribers, message.as_string())
        server.close()
        print('Email sent!')
    except Exception as e:
        print(e)
        print('Something went wrong...')


if __name__ == "__main__":
    alert_when_delta()
