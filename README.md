# Science Alliance Network

## MongoDB Installation

MongoDB URI: mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance
Username: allianceweb

## Required Packages

* PyMongo
* Flask-Mail

## Documentation

### Collection Structure

`users`: username, password, first, last, email, acct_type, school, primary
`fairs`: name, date, location, private
`registration`: user (id), fair (id), approved, permissions (array)

### Types

Account Types: Student, Mentor, Administrator

### Permission Settings

`is_owner`: owner of the fair
`full_access`: total access to controlling fair, except permission changes or delete