# Install

1. Install python 3.5. We suggest using a virtual environment if you know how.

2. Install MySQL and create a Database and a User who can access it

    Using SQL:
    ```
    CREATE DATABASE aiarena;
    CREATE USER aiarena INDENTIFIED BY 'aiarena';
    GRANT ALL PRIVILEGES ON aiarena.* TO aiarena WITH GRANT OPTION;
    ```

3. Install python modules
    ```
    pip install -r requirements.txt
    ```

4. Modify the Website config to use your Database

5. Initialize Website DB:
    ```
    python manage.py migrate
    python manage.py makemigrations
    ```

6. Create static files
   ```
   python manage.py collectstatic
   ```

7. Seed the database with data users and match data
    ```
    python manage.py seed
    ```

8. Launch the Website then navigate your browser to `http://127.0.0.1:8000/`
    ```
    python manage.py runserver
    ```
    You can log into the website using the accounts below:      
    Admin user: username - devadmin, password - x.  
    Regular user: username - devuser, password - x.