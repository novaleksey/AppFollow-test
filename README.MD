How to build and launch:
* docker-compose build
* docker-compose up -d

Check access on http://0.0.0.0:8080/posts

Available get params:

limit: positive number (default is 5)

offset: positive number (default is 0)

order: [ "id" | "url" | "title" | "created_at" ] (default is "id")

sort: [ "asc" | "desc" ] (default is asc)