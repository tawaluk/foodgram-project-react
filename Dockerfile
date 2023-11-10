version: '3.1'

volumes:

  pg_project: 'project'

services:
  pg_db:
    image: postgres
    restart: always
    environment:
      - POSTGRES_PASSWORD=secret
      - POSTGRES_USER=postgres
      - POSTGRES_DB=stage
    volumes:
      - pg_project:/var/lib/postgresql/data
    ports:
      - 5432:5432