# 设计文档

### 后端技术栈
- Python==3.9.6

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

建立3张表，Account（账户）, AuthProvider（身份验证）, Comment（留言）

- Account
  - id PK 主键
  - username str (unique) 用户名
  - email str (unique) 邮箱
  - updated_at datetime (UTC) 修改时间
  - created_at datetime (UTC) 创建时间

- AuthProvider
  - id PK 主键
  - auth_type str 验证方式(Password, Phone, WeChat, etc)
  - hashed_secret str (密码的密文)
  - updated_at datetime (UTC) 修改时间
  - created_at datetime (UTC) 创建时间

- Comment
  - id PK 主键
  - reply_id int 该留言的父级留言ID
  - content str 留言内容
  - account_id FK 账户ID
  - user_info JSON 留言的用户基本信息
  - updated_at datetime (UTC) 修改时间
  - created_at datetime (UTC) 创建时间

因为当前项目不涉及修改操作，所以 `updated_at` 字段略显多余。但一般情况下 `created_at` 与 `updated_at`
字段都是建表的基本字段，所以这里保留。

因为不涉及删除操作，所以没有添加表示逻辑删除的字段。

本项目的用户登陆方式只有 用户名/邮箱 + 密码这一种，所以 AuthProvider 表其实可以不需要，这里保留主要习惯。


### API 设计

- GET /healthz 探活
- GET /user 获取当前登陆用户的基本信息
- POST /register 新用户注册
- POST /login 用户登陆
- GET /comments 获取全部留言
- POST /comments 新建留言
- GET /redoc API 文档
- GET /docs API 文档


### 思路

由于本题目的难点在于树形留言支持无限嵌套，所以难点出现在以下几个方面：
- 数据库设计
- 数据检索
- 前后端数据交互
- 前端页面展示

在数据库设计上，这里选择的还是 MYSQL，原因是对 MYSQL 比较熟悉，并不是认为 NoSql 不适合本题。
在留言表设计的时候，通过 `id`, `reply_id` 这两个字段来生成最终的树形留言结构。

在留言表设计的时候，通过添加冗余字段 `user_info` 来减少数据库的查询次数。因为用户基本信息（用户名）等
属于很少变动的字段，而且如果变动了，可以通过异步刷数据来响应变动。

在实际测试中，对比过两种方案：
1. 留言表添加 `user_info` 冗余字段，避免再次查询该留言的用户基本信息。
2. 留言表不添加冗余字段，在查询该留言的用户基本信息的时候，通过外键 `account_id`获取用户基本信息。
   并且在查询的时候，采用 joinedload 的方式进行查询优化。

在 10000 条数据的情况下，方案 1 比方案 2 快约 0.1s（mysql Ver 8.0.28 for macos11.6 on x86_64 (Homebrew)）。
虽然差别不大，但最终选了了方案 1。


因为留言结构是树形的，而数据库存储的是展平的数据，所以需要将展平的数据转化为嵌套的结构，然后返回 json 格式的数据。
这一工作可以在后端做(返回给前端的 json 数据本身就是嵌套的结构）；
```json
[
  {
    "id": 1,
    "reply_id": null,
    "content": "comment 1",
    "sub_comments": [
      {
        "id": 2,
        "reply_id": 1,
        "content": "comment 2",
        "sub_comments": []
      }
    ]
  }
]
```
也可以在前端做（后端返回的 json 包含的数据没有做嵌套）。
```json
[
  {
    "id": 1,
    "reply_id": null,
    "content": "comment 1",
    "sub_comments": []
  },
  {
    "id": 2,
    "reply_id": 1,
    "content": "comment 2",
    "sub_comments": []
  }
]
```

但是通过测试发现由于 Python 支持的递归层级有限（Python >= 3.8.10 最大只支持 995 次递归，
而 JavaScript 则支持 11387 次递归 Chrome (101.0.4951.5)），所以最终选择由前端来转换
树形结构，后端返回原始的数据。这样就避免了后端在 jsonify 的时候报 `RecursionError`，虽然可以通过
`sys.setrecursionlimit` 来增大递归的层级，但是放宽限制可能引入其他的问题，所以没有采用。

由于前端很长时间没有碰了，不太熟悉，所以用了最简单的 Jquery 直接操作 Dom 的方式。


### 其他问题
- 为什么没有使用 Sqlite，而是 Mysql
  在使用 Mysql 开发完毕之后尝试将数据替换为 Sqlite，但是发现 Sqlite 不支持回滚，导致测试用例失败。
  期间尝试了设置 "PRAGMA journal_mode = OFF" 等，发现仍不起作用，所以最终放弃。
- 数据校验
  由于 FastApi 提供了 Pydantic，所以默认使用 Pydantic 做校验；
  对于 Pydantic 无法覆盖的场景，通过添加代码来实现。这样做最大的问题是
  Pydantic 默认给出的出错信息和用代码写的出错信息的格式不一致，这里需要单独处理。
- Session 与 Cookie
  由于采用了 JWT 来传递用户信息，所以服务端不需要存储 Session 信息。
- remember me 的实现
  由于这里没有安全方面的考虑，所以让前端来根据是否选择了 `remember me` 设置 cookie 的生命周期是会话级别的，还是 30 天之后过期。
- 测试
  这里使用 pytest 来做单元测试 + 集成测试，尽可能做到业务层的代码全覆盖。
