# Install

1. Install python 3.7 64 bit (these instructions might not work with 32 bit). We suggest using a virtual environment if you know how.

2. Install MySQL and create a Database and a User who can access it  
    Using SQL:
    ```
    CREATE DATABASE aiarena;
    CREATE USER aiarena IDENTIFIED BY 'aiarena';
    GRANT ALL PRIVILEGES ON aiarena.* TO aiarena WITH GRANT OPTION;
    ```

3. Install python modules
    ```
    python ./pip/pip-install.py
    ```
   The `pip-install.py` script runs a pip install using the generic and environment specific `requirements.txt` files.
   If you experience issues with it, you can simply run the commands manually instead:
   ```
   pip install -r ./pip/requirements.txt
   pip install -r ./pip/requirements.DEVELOPMENT.txt
   ```
   If these commands fail, then you likely have an issue with your environment (is `pip` in your PATH?).
   

4. Modify the Website config to use your Database.  
    If you are using a standard mysql setup at localhost:3306 and step 2's SQL script, then you can skip this step -
    the credentials will already be configured.  
    If you need to configure different credentials, make a copy of the `/aiarena/example-dev-env.py` file as 
    `/aiarena/env.py` and update the relevant details

5. Initialize Website DB:
    ```
    python manage.py migrate
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