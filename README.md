# nyt-book-viewer

View NYT Bestsellers

![Example of the page once the user has logged in and is viewing the books.](image.png)

Flask is used to serve all REST API requests, additionally it also serves the user interface.

All user data is stored on MongoDB Cloud Atlas and all book information is gathered from the NYT API. In order to run locally you need both a `mongo.key` and `nyt.key` file with their respective API keys in the `api` folder.


# API

Below is a short description of the API used.

## Auth

**Signup**

`/api/signup/`

- `uname`: username
- `pword`: password

Returns with response relating whether there was a successful signup. Additionally, if a successful signup occured the user will atain an authentication key.

**Login**

`/api/login/`

- `uname`: username
- `pword`: password

Returns with response relating whether there was a successful login. Additionally, if a successful login occured the user will atain an authentication key.

## Explore

**Explore**

`/api/explore/`

- `page_number`: integer you are requesting
- `category`: category being requested

Returns with response relating whether addition of rating occured or not.

## Review

**Rate**

`/api/rate/`

- `uname`: username
- `akey`: authentication key
- `isbn`: isbn number of book your review under it
- `review`: string with intended review in it
- `rating`: integer between 1 and 10

Returns with response relating whether addition of rating occured or not.

**Delete Rating**

`/api/deleterating/`

- `uname`: username
- `akey`: authentication key
- `isbn`: isbn number of book your review under it

Returns with response relating whether deletion of rating occured or not.

## Comment

**Comment**

`/api/comment/`

- `uname`: username
- `akey`: authentication key
- `isbn`: isbn number of book with comment of review under it
- `review_uname`: username of reviewer you commented under
- `comment`: comment content you are adding

Returns with response relating whether deletion occured or not.

**Delete Comment**

`/api/deletecomment/`

- `uname`: username
- `akey`: authentication key
- `isbn`: isbn number of book with comment of review under it
- `review_uname`: username of reviewer you commented under
- `comment`: comment content you are deleting

Returns with response relating whether deletion occured or not.

**Alter Comment**

`/api/altercomment/`

- `uname`: username
- `akey`: authentication key
- `isbn`: isbn number of book with comment of review under it
- `review_uname`: username of reviewer you commented under
- `comment`: comment content you are altering
- `updated_comment`: updated comment content you are altering too

Returns with response relating whether success occured or not.

## Other

**Ping**

`/api/ping/`

pong


# TODO

- [ ] Create API
	- [x] End point username / password
	- [ ] Allow searching the data source
	- [x] Allow rating system
		- [x] Must support create, read, update, delete operations
	- [x] Comment system
- [ ] Create UI
	- [ ] End point username / password
	- [ ] Allow searching the data source
	- [ ] Allow rating system
		- [ ] Must support create, read, update, delete operations
	- [ ] Comment system
