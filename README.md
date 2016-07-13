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
`pairings`: fair (id), student (id), mentor (id)

### Types

Account Types: Student, Mentor, Administrator

### Permission Settings

`is_owner`: owner of the fair
`full_access`: total access to controlling fair, except permission changes or delete
`can_approve_users`: allowed to approve users to fair
`can_pair_users`: allowed to pair users together