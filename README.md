# Tiny-Backspace

## API Documentation

The following section will give a detailed description about the various endpoints and their usage in the Tiny-Backspace application. It also includes examples on how to use `curl` command to access the APIs and the response format.

### Creating a new Short URL

To create a new short URL, use the following endpoint:

`POST /createUrl`

#### Request

The request body should be a JSON object with the following format:

    {
        "url": "string"
    }

Example:

    curl -X POST -H "Content-Type: application/json" -d '{"url":"https://example.com"}' http://localhost:3000/createUrl

#### Response

The response body will be a JSON object with the following format:

    {
        "shortUrl": "string"
    }

Example:

    {
        "shortUrl": "http://localhost:3000/1a2b3c"
    }

### Redirect to Original URL

To be redirected to the original URL of a short URL, use the following endpoint:

`GET /:shortUrl`

#### Request

No request body is needed. You just need to replace `:shortUrl` with the actual short URL's ID.

Example:

    curl -X GET http://localhost:3000/1a2b3c

#### Response

The response will be a 302 redirect to the original URL.

### Getting URL Statistics

To get the statistics of a URL, use the following endpoint:

`GET /:shortUrl/stats`

#### Request

No request body is needed. You just need to replace `:shortUrl` with the actual short URL's ID.

Example:

    curl -X GET http://localhost:3000/1a2b3c/stats

#### Response

The response body will be a JSON object with the following format:

    {
        "url": "string",
        "clicks": "number"
    }

Example:

    {
        "url": "http://localhost:3000/1a2b3c",
        "clicks": 123
    }