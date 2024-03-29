# ProjPlag

## Instalando a aplicação:

- Verificar se tem Python3, Pip3 e Java rodando em seu servidor

- Lista de bibliotecas para serem instaladas com ``pip3 install``:

``flask``
``flask_bootstrap``
``flask_sqlalchemy``
``flask_wtf``
``sqlalchemy``
``wtforms``
``wtforms.validators``
``werkzeug.utils``
``python-decouple``
``pymysql``
``python-dotenv``
``pandas``

- Instalação mysql:
  
    ```
    $sudo apt update
    $sudo apt install mysql-server
    $sudo mysql
    mysql>CREATE USER '<usuario-bd>'@'localhost' IDENTIFIED BY '<senha-usuario-bd>';
    mysql>CREATE DATABASE <nome-bd>;
    mysql>GRANT ALL PRIVILEGES ON <nome-bd>.* to '<usuario-bd>'@'localhost';
    mysql>exit;
    ```

É possivel acessar o banco de dados com o usuário criado, usando o comando:

``mysql -u <usuario-bd> -p``

Será necessário criar o arquivo ``src/.env`` com o seguinte conteúdo:
   
    
    CONNECT_STRING=mysql+pymysql://<usuario-bd>:<senha-bd>@localhost/<nome-bd>
    FILE_KEY=ultrasecretkey
    

A senha do FILE_KEY é usada para upload de arquivos, pode definir a que preferir

A aplicação é iniciada com o comando ``python3 app.py`` dentro da pasta src/

Será acessivel na url: localhost:5000/
