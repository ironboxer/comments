
本项目使用了 Mysql 作为后端存储，而 Mysql 的安装与配置比较麻烦，所以如果需要本地启动，
建议使用 docker-compose 的方式 来启动： `docker-compose up --build` 。
首次启动时间较长，大概需要等待 10 分钟。
因为采用了 docker-compose 启动，所以无法做到在启动的时候自动打开浏览器。


如果需要在本地开发调试，可以按照以下步骤：
1. 安装 Python 3.9.6 及 Mysql 8
2. 创建并初始化项目虚拟环境： `python -m venv .venv && source .venv/bin/activate`
3. 安装本项目依赖：`make dev`
4. 启动本地开发环境：`make dev-server`
5. 测试：`make test` 及 `make ci-test`

注：本地已安装的 mysql 用户名密码等信息一般都不一样，可以修改 .env 文件来适配本项目。

.env
```dotenv
COMMENT_MYSQL_HOST="your mysql host"
COMMENT_MYSQL_USER="your mysql username"
COMMENT_PASSWORD="your mysql password"
COMMENT_MYSQL_PORT="your mysql port"
COMMENT_MYSQL_DB="your mysql db"
```

项目启动时，会自动生成一个用户和 1001 条该用户的评论。用户信息：
- username: User1
- email: user1@foo.bar
- password: A1#dsa12
