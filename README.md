# Renderer

Accepts PDF files and renders the pages to normalized PNG files that fit into 1200x1600 pixels rectangle.

## WIP

Unfortunately it is still work in progress. I don't have time to finish this project now. No testing has been done,
so I expect there to be errors and problems with running. I apologize for that.

## API

Quick description of the API endpoints.

### POST `/documents`

* accepts a PDF file
* returns its `uuid`

### GET `/documents/<string:uuid>`

* accepts `uuid`
* returns `uuid`, `ready` status and number of `pages`

### GET `/documents/<string:uuid>/<int:page>`

* accepts `uuid` and `page` number
* returns the PNG image
* NOTE: only available if the status flag `ready` is true
