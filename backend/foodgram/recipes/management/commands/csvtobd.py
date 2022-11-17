import csv
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Заполняет БД модели из csv'

    def add_arguments(self, parser):
        parser.add_argument('model', nargs='+', type=str)
        parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):
        model = options['model'][0]
        file = options['file'][0]
        models = {'Ingredient': Ingredient}
        with open(
            f'{os.getcwd()}/../../data/{file}',
            newline='', encoding='utf-8'
        ) as op_file:
            reader = csv.reader(op_file)
            for i, row in enumerate(reader):
                if row[0] == 'name':
                    fields = ['id'] + row[:]
                else:
                    values = {}
                    for j in range(len(row) + 1):
                        values[fields[j]] = i if j == 0 else row[j - 1]
                    models[model].objects.get_or_create(**values)

                    print(models[model].objects.get(id=i))
