# 业务服务

Spring Boot 业务服务为前端提供以下一期接口：

- `GET /api/v1/programs`：按关键词、地区、专业代码、408/自命题等考试科目筛选。
- `GET /api/v1/programs/{id}`：获取院校专业详情。
- `PUT /api/v1/profiles/{userId}`：保存计算机考研学生画像。
- `GET /api/v1/profiles/{userId}`：读取学生画像。
- `POST/GET /api/v1/favorites`：收藏与读取目标项目。
- `POST /api/v1/admin/imports/programs`：导入招生项目 CSV。

启动：

```powershell
mvn spring-boot:run
```

演示环境使用 H2 内存数据库。迁移到 MySQL 时，对照仓库根目录的 `database/schema.sql` 配置数据源即可。
