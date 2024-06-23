source: https://stackabuse.com/running-airflow-locally-with-docker-a-technical-guide/

Введение
Apache Airflow и Docker - два мощных инструмента, которые произвели революцию в способах обработки данных и развертывания программного обеспечения. Apache Airflow - это платформа с открытым исходным кодом, которая позволяет программно создавать, планировать и контролировать рабочие процессы. Docker, с другой стороны, представляет собой платформу, которая позволяет разработчикам упаковывать приложения в контейнеры — стандартизированные исполняемые компоненты, объединяющие исходный код приложения с библиотеками операционной системы и зависимостями, необходимыми для запуска этого кода в любой среде.

Локальный запуск Airflow с помощью Docker - отличная идея по нескольким причинам. Во-первых, Docker предоставляет изолированную и согласованную среду для настройки Airflow, снижая вероятность возникновения проблем из-за различий в зависимостях, библиотеках или даже операционной системе. Во-вторых, Docker упрощает версификацию, распространение и репликацию вашей настройки Airflow, что может быть особенно полезно в командной среде или при переходе от разработки к производству.

Настройка локальной среды
Чтобы начать, на вашем компьютере должно быть установлено следующее программное обеспечение:

Python (версия 3.6 или новее)
Docker (версия 20.10.11)
Docker Compose (версия 2.2.1)
Установка Python, Docker и Airflow проста. Для Python и Docker вы можете следовать официальному руководству по установке для вашей конкретной ОС. Для Airflow вы можете установить его с помощью pip, программы установки пакетов Python.

Установите Python
Apache Airflow написан на Python, поэтому на вашем компьютере должен быть установлен Python. Вы можете загрузить его с официального веб-сайта Python. На момент написания статьи для Airflow требуется Python 3.6 или выше.

Чтобы проверить, установлен ли Python, и посмотреть его версию, откройте окно терминала и введите:

$ python --version
Установите Docker
Docker позволяет нам размещать наши настройки Airflow в контейнерах. Вы можете загрузить Docker с официального веб-сайта Docker. Выберите версию, подходящую для вашей операционной системы.

После установки вы можете проверить, правильно ли установлен Docker, открыв окно терминала и набрав:

$ docker --version
Установите Docker Compose
Docker Compose - это инструмент, который позволяет нам определять многоконтейнерные приложения Docker и управлять ими, что и будет нашей настройкой Airflow. Обычно он входит в комплект установки Docker на Windows и Mac, но в некоторых дистрибутивах Linux его может потребоваться установить отдельно. Вы можете проверить, установлен ли Docker Compose, и просмотреть его версию, набрав:

$ docker-compose --version
Если он не установлен, вы можете следовать официальному руководству по установке Docker Compose.

Структура проекта
Рекомендуется хранить все файлы, связанные с Airflow, в выделенном каталоге, чтобы поддерживать чистую и организованную структуру проекта.

Вот предлагаемая структура для вашего проекта:

my_project/
│
├── airflow/                  # Directory for all Airflow-related files
│   ├── dags/                 # Directory to store your Airflow DAGs
│   │   ├── dag1.py
│   │   ├── dag2.py
│   │   └── ...
│   │
│   ├── Dockerfile            # Dockerfile for building your custom Airflow image
│   ├── docker-compose.yml    # Docker Compose file for defining your services
│
└── ...                       # Other directories and files for your project
В этой структуре:

В airflow/ каталоге хранятся все файлы, связанные с Airflow. Это позволяет отделить настройку Airflow от остальной части вашего проекта, упрощая управление.

В dags/ каталоге внутри airflow/ каталога хранятся ваши базы данных Airflow. Это скрипты Python, которые определяют ваши рабочие процессы. В вашем файле Docker Compose вы должны сопоставить этот каталог с /usr/local/airflow/dags в ваших контейнерах Airflow.

Каталог Dockerfile внутри airflow/ используется для создания пользовательского образа Airflow Docker. Этот файл будет содержать инструкции по инициализации базы данных Airflow и копированию вашего пользовательского airflow.cfg файла в изображение.

В docker-compose.yml файле внутри airflow/ каталога вы определяете свои службы (веб-сервер, планировщик, базу данных и т.д.) Для Docker Compose.

Персонализация вашего Airflow-Настройка Docker
Прежде чем вы сможете запустить Airflow, вам необходимо инициализировать его базу данных. При настройке с использованием Docker инициализация базы данных Airflow и настройка airflow.cfg файла могут выполняться в контейнере Docker, а не на хост-компьютере.

Для этого вы можете использовать Dockerfile для создания пользовательского образа Airflow Docker. В этом файле Dockerfile вы можете указать команды для инициализации базы данных Airflow и настройки airflow.cfg файла.

Вот пример файла Dockerfile:

# Use the official Airflow image as the base
FROM apache/airflow:latest

# Set the AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/usr/local/airflow

# Switch to the root user
USER root

# Create the AIRFLOW_HOME directory and change its ownership to the airflow user
RUN mkdir -p ${AIRFLOW_HOME} && chown -R airflow: ${AIRFLOW_HOME

# Switch back to the airflow user
USER airflow

# Initialize the Airflow database
RUN airflow db init

# Customize the airflow.cfg file
RUN echo "[core]" > ${AIRFLOW_HOME}/airflow.cfg && \
    echo "airflow_home = ${AIRFLOW_HOME}" >> ${AIRFLOW_HOME}/airflow.cfg && \
    echo "executor = LocalExecutor" >> ${AIRFLOW_HOME}/airflow.cfg && \
    echo "" >> ${AIRFLOW_HOME}/airflow.cfg && \
    echo "[webserver]" > ${AIRFLOW_HOME}/airflow.cfg && \
    echo "base_url = http://localhost:8080" >> ${AIRFLOW_HOME}/airflow.cfg && \
    echo "web_server_host = 0.0.0.0" >> ${AIRFLOW_HOME}/airflow.cfg && \
    echo "web_server_port = 8080" >> ${AIRFLOW_HOME}/airflow.cfg{AIRFLOW_HOME}/airflow.cfg
В этом файле Dockerfile мы сначала устанавливаем для AIRFLOW_HOME переменной окружения значение /usr/local/airflow. Затем мы переключаемся на пользователя root с помощью USER root директивы. Это необходимо, потому что нам нужны права root для создания каталога и смены владельца.

Далее мы создаем AIRFLOW_HOME каталог и меняем его владельца на airflow пользователя. Это делается с помощью RUN mkdir -p ${AIRFLOW_HOME} && chown -R airflow: ${AIRFLOW_HOME} команды. -p Опция в mkdir команде гарантирует, что каталог будет создан, если он не существует.

После этого мы переключаемся обратно на airflow пользователя, используя USER airflow директиву. Это хорошая практика из соображений безопасности, поскольку запуск контейнеров от имени пользователя root может представлять угрозу безопасности.

Затем мы инициализируем базу данных Airflow с помощью RUN airflow db init команды.

Наконец, мы настраиваем airflow.cfg файл непосредственно в контейнере Docker. Это делается с помощью RUN директивы с серией echo команд, которые добавляют наши пользовательские настройки к airflow.cfg файлу. Этот подход позволяет нам настраивать airflow.cfg файл без необходимости создавать и настраивать файл на хост-компьютере.

В этом файле Dockerfile мы используем > оператор вместо >> operator при первой записи в airflow.cfg файл. > Оператор перезаписывает файл указанным текстом, в то время как >> оператор добавляет текст к файлу. Перезаписывая файл, мы гарантируем, что каждый раздел будет объявлен только один раз.

Вот пример того, как будут выглядеть ваши airflow.cfg настроенные разделы в файле:

[core]
# The home directory for Airflow
airflow_home = ~/airflow

# The executor class that Airflow should use. Choices include SequentialExecutor, LocalExecutor, and CeleryExecutor.
executor = LocalExecutor

[webserver]
# The base URL for your Airflow web server
base_url = http://localhost:8080

# The IP address to bind to
web_server_host = 0.0.0.0

# The port to bind to
web_server_port = 8080
После создания этого файла Dockerfile вы можете создать свой пользовательский образ Airflow Docker с помощью docker build команды. Вот пример:


Бесплатная электронная книга: Основы Git
Ознакомьтесь с нашим практическим руководством по изучению Git с рекомендациями, принятыми в отрасли стандартами и прилагаемой шпаргалкой. Перестаньте гуглить команды Git и действительно изучите это!


Загрузите электронную книгу
 
$ docker build -t my-airflow-image .
Docker Compose
Docker Compose - это инструмент, позволяющий определять многоконтейнерные приложения Docker и управлять ими. Он использует файл YAML для указания служб, сетей и томов вашего приложения, а затем запускает все эти компоненты одной командой.

Настройка файла Docker Compose
В файле Docker Compose вы определяете службы вашего приложения. Для Airflow базовый файл Docker Compose может включать службы для веб-сервера, планировщика и базы данных. Этот файл должен находиться в том же каталоге, что и ваш Dockerfile.

Вот пример:

version: "3"
services:
  webserver:
    build:
      context: .
      dockerfile: Dockerfile
    command: webserver
    volumes:
      - ./dags:/usr/local/airflow/dags
    ports:
      - "8080:8080"
  scheduler:
    build:
      context: .
      dockerfile: Dockerfile
    command: scheduler
    volumes:
      - ./dags:/usr/local/airflow/dags
  postgres:
    image: postgres:latest
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
      
В этом файле Docker Compose мы определяем три службы: webserver, scheduler и postgres. Директива build предписывает Docker Compose создать образ, используя Dockerfile в текущем каталоге. volumes Директива сопоставляет ./dags каталог на вашем хост-компьютере с /usr/local/airflow/dags каталогом в контейнере Docker, позволяя вам хранить ваши базы данных на вашем хост-компьютере. Директива ports сопоставляет порт 8080 на вашем хост-компьютере с портом 8080 в контейнере Docker, позволяя вам получить доступ к веб-серверу Airflow по адресу http://localhost:8080.

postgres Сервис использует postgres:latest образ и устанавливает переменные среды непосредственно в файле Docker Compose. Эти переменные среды используются для настройки базы данных Postgres.

Запуск сервисов Airflow
Чтобы запустить службы Airflow, вы можете использовать docker-compose up команду. Добавление -d флага запускает службы в фоновом режиме. Вот команда:

$ docker-compose up -d
Эта команда запустит все службы, определенные в вашем файле Docker Compose. Вы можете проверить состояние своих служб с помощью docker-compose ps команды.

Создание пользователя в Airflow
После настройки Docker compose с помощью Airflow вам нужно будет создать пользователя, который сможет получить доступ к веб-интерфейсу Airflow. Это можно сделать, выполнив команду в запущенном контейнере Docker.

Сначала вам нужно найти идентификатор контейнера вашего запущенного веб-сервера Airflow. Вы можете сделать это, выполнив следующую команду:

$ docker ps
В этой команде перечислены все запущенные контейнеры Docker и их сведения. Найдите контейнер, в котором запущен веб-сервер Airflow, и запишите его идентификатор контейнера.

Далее вы можете создать нового пользователя в Airflow, выполнив следующую команду:

$ docker exec -it <container-id> airflow users create --username admin --password admin --firstname First --lastname Last --role Admin --email admin@example.com
Замените <container-id> идентификатором контейнера, который вы указали ранее. Эта команда создает нового пользователя с именем пользователя "admin", паролем "admin", именем "First", фамилией "Last", ролью "Admin" и электронной почтой "admin@example.com". Вам следует заменить эти значения своими собственными.

После выполнения этой команды вы сможете войти в веб-интерфейс Airflow, используя учетные данные только что созданного вами пользователя.

Оптимизация и приложения
Повышение производительности
Оптимизация Airflow и настроек Docker может значительно повысить производительность вашего конвейера передачи данных. Что касается Airflow, рассмотрите возможность использования LocalExecutor для параллельного выполнения задач и точной настройки DAG, чтобы сократить количество ненужных задач. Для Docker убедитесь, что ваши изображения максимально облегчены, и используйте встроенные функции управления ресурсами Docker, чтобы ограничить использование процессора и памяти.

Например, вы можете ограничить использование памяти вашими контейнерами Docker, добавив mem_limit параметр в файл Docker Compose:

services:
  webserver:
    build:
      context: .
      dockerfile: Dockerfile
    command: webserver
    volumes:
      - ./dags:/usr/local/airflow/dags
    ports:
      - "8080:8080"
    mem_limit: 512m
Помимо памяти, вы также можете управлять ресурсами процессора, которые может использовать контейнер, установив параметр cpu_shares:

services:
  webserver:
    build:
      context: .
      dockerfile: Dockerfile
    command: webserver
    volumes:
      - ./dags:/usr/local/airflow/dags
    ports:
      - "8080:8080"
    mem_limit: 512m
    cpu_shares: 512
Параметр cpu_shares позволяет управлять ресурсами процессора, которые может использовать контейнер. Значение представляет собой относительный вес по сравнению с другими контейнерами. Например, если один контейнер имеет значение 1024, а другой - 512, первый контейнер получит вдвое больше процессорного времени, чем второй.

Это простое дополнение может оказать глубокое влияние на производительность вашей системы, гарантируя эффективное использование ваших ресурсов и бесперебойную работу конвейера передачи данных. Именно эти небольшие настройки и оптимизации могут иметь большое значение в долгосрочной перспективе, превращая хороший конвейер данных в отличный.

Когда и почему я использую Airflow с помощью Docker
За время моей работы инженером по обработке данных у меня была возможность поработать над множеством сложных проектов. Один из таких проектов включал создание конвейера данных для обработки и анализа больших объемов данных. Сложность проекта была огромной, и потребность в инструменте, который мог бы упростить процесс, была очевидна. Именно тогда я открыл для себя Airflow и Docker.

Airflow с его надежными возможностями планирования и оркестровки идеально подходил для наших потребностей в конвейере данных. Однако по-настоящему кардинальным стал Docker. Docker позволил нам контейнеризировать нашу систему Airflow, что принесло множество преимуществ.

Во-первых, Docker невероятно упростил совместную работу с моей командой. Мы смогли поделиться нашими изображениями Docker и убедиться, что все работают в одной среде. Это устранило проблему "но это работает на моей машине" и сделало наш процесс разработки намного более плавным.

Во-вторых, Docker позволил нам легко тестировать наши конвейеры Airflow на наших локальных компьютерах. Мы могли локально тиражировать нашу производственную среду, запускать наши конвейеры и выявлять любые проблемы на ранних этапах процесса разработки. Это было значительным улучшением по сравнению с нашим предыдущим рабочим процессом, где тестирование было громоздким процессом.

Наконец, когда пришло время развертывать наши конвейеры на производстве, Docker сделал процесс плавным. Нам просто нужно было отправить наш образ Docker на производственный сервер и запустить его. Не нужно было беспокоиться об установке зависимостей или настройке сервера. Все, что нам было нужно, было упаковано в наш образ Docker.

Использование Airflow в Docker изменило наш опыт. Это не только сделало наш процесс разработки более эффективным, но и позволило нам создать высококачественный конвейер данных, соответствующий потребностям нашего проекта. Я бы настоятельно рекомендовал эту настройку любому разработчику или команде, работающим над проектами data pipeline.

Тематическое исследование: рабочий процесс анализа данных Quizlet
Внедрение Quizlet Apache Airflow произвело революцию в их ETLS для аналитики. Компания Airflow, изначально развернутая на одном сервере, упростила извлечение данных из Google BigQuery, запуск аналитики в SQL и сохранение результатов для отчетов и информационных панелей. Успех этого развертывания привел к расширению круга задач, включая обучение классификаторам машинного обучения, расчет поисковых индексов, A / B тестирование и таргетинг на пользователей.

В перспективе Quizlet планирует улучшить развертывание Airflow путем переноса базы данных метаданных в выделенный экземпляр, интеграции с облачным хранилищем Google и перехода на распределенную систему массового обслуживания. По сути, Apache Airflow изменил правила игры для Quizlet, позволив им делать больше и продвигать свой бизнес вперед.

Заключение
В этой статье мы рассмотрели, как локально запустить Airflow с помощью Docker. Мы рассмотрели все, начиная с настройки локальной среды и установки необходимого программного обеспечения и заканчивая развертыванием служб Airflow с помощью Docker Compose. Мы также обсудили несколько советов и хитростей по оптимизации вашей настройки и поделились личным опытом и реальными приложениями.

Запуск Airflow с помощью Docker обеспечивает согласованную изолированную среду, которая может быть легко версифицирована, распространена и реплицирована. Эта настройка идеально подходит для управления сложными конвейерами данных, поскольку сочетает мощные возможности планирования и оркестровки Airflow с гибкостью и изоляцией Docker. Являетесь ли вы инженером по обработке данных, стремящимся оптимизировать свои рабочие процессы, или командой, стремящейся обеспечить согласованность в вашей среде разработки, локальный запуск Airflow с помощью Docker - мощное решение.

Я надеюсь, что это руководство было полезным и дало вам знания и уверенность, необходимые для начала вашей собственной настройки Airflow-Docker.