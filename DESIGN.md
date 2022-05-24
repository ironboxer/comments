# 设计文档

### 思路

由于本题目的难点在于树形留言支持无限嵌套，所以难点出现在以下几个方面：
- 数据库设计
- 数据检索
- 前后端数据交互
- 前端页面展示

在数据库设计上，这里选择的还是 RDBMS（MYSQL），原因是对MYSQL比较熟悉，并不是认为NoSql不适合本题。
在留言表设计的时候，通过 `id`, `reply_id` 这两个字段来生成最终的树形留言结构。

在留言表设计的时候，通过添加冗余字段 `user_info` 来减少数据库的查询次数。因为用户基本信息（用户ID，用户名）等
属于很少变动的字段，而且如果变动了，可以通过异步刷新数据来应用变动。

在实际测试中，对比过两种方案：
1. 留言表添加 `user_info` 冗余字段，避免再次查询该留言的用户基本信息
2. 留言表不添加冗余字段，在查询该留言的用户基本信息的时候，通过外键 `account_id`获取用户基本信息，
只不过在查询的时候，采用 joinedload 的方式来获取关联用户的基本信息。

在10000条数据的情况下，方案1比方案2快约0.1s（mysql  Ver 8.0.28 for macos11.6 on x86_64 (Homebrew)）。
所以最终选了了方案1。


因为留言结构是树形的，而数据库存储的是展平的数据，所以需要将展平的数据转化为嵌套的结果。
这一工作可以在后端做，然后返回给前端的数据就是树形的；也可以在前端做，后端只返回原始的数据。

但是通过测试发现由于 Python 支持的递归层级有限（Python >= 3.8.10 最大只支持 995 次递归，
而 JavaScript 则支持 11387 次递归 Chrome (101.0.4951.5)），所以最终选择由前端来转换
树形结构，后端返回原始的数据。这样就避免了后端在 jsonify 的时候报 `RecursionError`，虽然可以通过
`sys.setrecursionlimit` 来增大递归的层级，但是放宽限制可能引入其他的问题，所以没有采用。


由于前端很长时间没有碰了，所以用了最简单的 Jquery 直接操作 DOM 的方式。CSS 更是不会写，
所以前端确实很丑。


### 其他问题
- 数据校验
  由于 FastApi 提供了 Pydantic，所以默认使用 Pydantic 做校验；
  对于 Pydantic 无法覆盖的场景，通过添加代码来实现。这样做最大的问题应该是
  Pydantic 默认给出的出错信息和用代码写的出错信息的格式不一致，这里需要单独处理。
- remember me 的实现
  由于这里考察的不是安全方面，所以让前端来根据是否选择了 `remember me` 设置 cookie 的生命周期是会话级别的，还是 30 天之后过期。
- 测试
  这里使用 pytest 来做单元测试 + 集成测试，尽可能做到业务层的代码全覆盖。


### 后端技术栈

- FastAPI
  - pydantic: API data schema
  - Auth: OAuth2 + JWT

- Package Management
  - pip-compile + requirements.in

- Database
  - MySQL 8.0
  - SQLAlchemy
  - Alembic (migration)

- Web Server
  - Uvicorn + uvloop

- Testing
  - pre-commit
  - Unit / Integration Test: pytest


### 模型设计

建立3张表，User（账户）, AuthProvider（身份验证）, Comment（留言）

- User
  - id PK 主键
  - username str (unique) 用户名
  - email str (unique) 邮箱
  - updated_at datetime (UTC) 修改时间
  - created_at datetime (UTC) 创建时间

- AuthProvider
  - id PK 主键
  - auth_type str 验证方式(PASSWORD, Phone, WeChat, etc)
  - hashed_secret str (密码的密文)
  - updated_at datetime (UTC) 修改时间
  - created_at datetime (UTC) 创建时间

- Comment
  - id PK 主键
  - reply_id int 留言的父级留言ID
  - content str 留言内容
  - account_id FK 账户ID
  - user_info JSON 留言的用户基本信息
  - updated_at datetime (UTC) 修改时间
  - created_at datetime (UTC) 创建时间


### API 设计

- GET /healthz livenessProbe
- GET /user 获取登陆用户基本信息
- POST /register 新用户注册
- POST /login 用户登陆
- GET /comments 获取全部留言
- POST /comments 新建留言
