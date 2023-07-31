
  
<!-- PROJECT -->  
<p align="center">  
  <h3 align="center">   
   Creating an complete authentication to your API. 
  </h3>   
</p>  
  
<!-- ABOUT THE PROJECT -->  
## 🤔 Introduction  
You are going to have these functions:
- Login (auth/token)
- SignUp
- Reset Password
- Send Random code by email
- Validade code
  
<br />   
  
  
<!-- INSTALLATION -->  
  

> If you are on Linux use `python3 uvicorn:app` to run the application
> and to install new libraries use `pip3 install libraryname`

 
  
# 🔨 Installation and Running

Install the required dependencies by running:
  
1. Create account in https://signup.sendgrid.com/, and create your API_KEY following the tutorial https://www.loom.com/share/aaa6b7dfdaf046ae915dfcfd0c325c1e?sid=adcbdd61-67af-4d73-8f1a-0d0f4e54e8a2 

2. Still on SendGrid you need to go on https://app.sendgrid.com/settings/sender_auth and setup your email as sender.(Because you can use on the `from` parameter on your code this email.)

3. You should have the API_KEY and the sender email to use in yours `SECRETS`.

5. Run the file `creation_script.sql` on your database.WARNING: it is deleting tables user,user_code and user role if exist.(If you dont have database you can follow the extra instructions to create your docker database.)

4. Clone this repository  
  
5. Set `SECRETS` as enviroment variable with our  sample `secrets_model.json`.

6. Install the requirements running  `pip install -r requirements.txt`  

7. Run the following command in the `python uvicorn:app"`

Extra Steps (Mysql On docker)
Reference: https://hub.docker.com/_/mysql

1. Run the command to download and run the docker ` docker run --name mysql-db -e MYSQL_ROOT_PASSWORD=admin -d mysql:latest`

2. I already put on our `secrets_sample.json` most of things as localhost you just need to change the `password`

3.  I strongly recommend to use https://dbeaver.io/
to connect in your database.

<br />  
  
## 📚 Project Files Overview

- `main.py`: The main file to run and call the REST API.
- `requirements.txt`: A file containing project dependencies.
- `database.py`: A class with mysql database connection.
- `email_grid.py`: A class with generic functions to send email using SendGrid.

- `secret.py`: Class that consume your `SECRETS` and share with the whole project.

- `models.csv`: A class with the sqlalchemy and Pydantic to manage the data typing and tables interaction in your API.

- `.gitignore`: Defines files that should be ignored by Git.
- `Dockerfile`: A Sample to show how to run your Fast API on docker.

## 🔓 Author and Acknowledgements

- **Author**: [Paulo Mota](https://www.linkedin.com/in/paulo-mota-955218a2/)<br>
-**Testing library**:: [Chispa](https://github.com/MrPowers/chispa)<br>

