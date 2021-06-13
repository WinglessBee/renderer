# Renderer

Accepts PDF files and renders the pages to normalized PNG files that fit into 1200x1600 pixels rectangle.

## Dependencies

Docker and docker-compose need to be installed and ready.

## Quick Start

Clone the repository and run the Renderer with the following command:

```
docker-compose up
```

OpenAPI is running on http://localhost:5000/

Enjoy uploading PDF files and downloading PNG images! 😊

## API

Quick description of the API endpoints.

### POST `/documents`

* accepts a PDF file
* returns its `uuid`

### GET `/documents/<string:uuid>`

* accepts `uuid`
* returns `uuid`, status flag `ready`, and number of `pages`

### GET `/documents/<string:uuid>/<int:page>`

* accepts `uuid` and `page` number
* returns the PNG image
* NOTE: only available if the status flag `ready` is *true*

## Error Handling

Flask and its worker task may exit a couple of times before Postgres starts. Docker will restart both automatically.

If an error occurs during a PDF file conversion, the status flag `ready` is set to *false*. If the file has not been
processed yet, the status flag `ready` is *null*.
