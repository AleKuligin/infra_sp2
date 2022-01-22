import csv
import os
from datetime import datetime
import pytz

from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


class Command(BaseCommand):
    help = 'Add data from CSV-file to database. Args: <file.csv> <model>'

    def import_to_db(self, file, model, *args):
        path_dir = 'static/data/'
        path = path_dir + file
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                object_dict = {}
                for row in reader:
                    dict = {
                        key: value for key, value in zip(header, row)
                    }
                    for key, value in dict.items():
                        if key == 'category':
                            value = Category.objects.get(id=value)
                        if key == 'title_id':
                            key = 'title'
                            value = Title.objects.get(id=value)
                        if key == 'author':
                            value = User.objects.get(id=value)
                        if key == 'review':
                            value = Review.objects.get(id=value)
                        if key == 'genre_id':
                            key = 'genre'
                            value = Genre.objects.get(id=value)
                        if key == 'pub_date':
                            value = datetime.strptime(
                                value, "%Y-%m-%dT%H:%M:%S.%fZ"
                            )
                            value = pytz.utc.localize(value)
                        object_dict[key] = value
                    model.objects.get_or_create(**object_dict)

    def handle(self, *args, **kwargs):

        self.import_to_db(file='category.csv', model=Category)
        self.import_to_db(file='genre.csv', model=Genre)
        self.import_to_db(file='users.csv', model=User)
        self.import_to_db(file='titles.csv', model=Title)
        self.import_to_db(file='review.csv', model=Review)
        self.import_to_db(file='comments.csv', model=Comment)
        self.import_to_db(file='genre_title.csv', model=GenreTitle)

        self.stdout.write(self.style.SUCCESS(
            'CSV-files are successfully imported'))
