# Polls app API

Polls app for conducting surveys about different test products.

The goal is for users to make survey for test product and collect information easily and in one place.
Products are sent to company offices or customers with a QR code containing the link for the product.

# Set up

- To start this in Docker you need to create **env** folder and add 3 files:

  - django.env:

        SECRET_KEY=<your secret key>
        DEBUG=1
        ALLOWED_HOSTS=localhost
        DATABASE_NAME=<your db_name>
        DATABASE_USER=<your postgres user>
        DATABASE_PASSWORD=<your postgres password>
        DATABASE_HOST=postgresql
        DATABASE_PORT=5432
        EMAIL_HOST_USER=<your@mail.host>
        EMAIL_HOST_PASSWORD=<your password>

  - postgres.env:

        POSTGRES_USER=<your postgres user>
        POSTGRES_PASSWORD=<your postgres password>
  
  - postgres.env:
      
        PGADMIN_DEFAULT_EMAIL=pgadmin@email.com
        PGADMIN_DEFAULT_PASSWORD=pgadmin