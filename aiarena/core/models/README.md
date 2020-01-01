# Models
Each model is contained in its own file.

## Creating a new model
- Create the new model in it's own file. Name the file the same as the model.
- Import the new model in `__init__.py`. This will allow django to find it.
- Run `python manage.py makemigrations` to generate the database migration for the new model.