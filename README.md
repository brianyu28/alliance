# Science Alliance Network

## MongoDB Installation

MongoDB URI: mongodb://allianceweb:crbysj2016!!@ds011765.mlab.com:11765/alliance
Username: allianceweb

## Required Packages

* PyMongo
* Flask-Mail
* pytz (timezone)

## Documentation

### Collection Structure

`users`: username, password, first, last, email, acct_type, school, primary, primary_partner
`fairs`: name, date, location, private
`registration`: user (id), fair (id), approved, permissions (array)
`pairings`: fair (id), student (id), mentor (id)
`trainings`: fair (id), mentor (id), trainer (id)
`announcements`: fair (id), author (id), title, contents

### Types

Account Types: Student, Mentor, Administrator

### Permission Settings

`is_owner`: owner of the fair
`full_access`: total access to controlling fair, except permission changes or delete
`can_approve_users`: allowed to approve users to fair
`can_pair_users`: allowed to pair users together
`can_pair_trainers`: can assign mentor trainers

Access Levels:

`Owner`: Owns fair, has full access and control
`Full Access`: Full access to fair
`Partial Access`: Has some permissions (pair users, pair trainers, approve users)
`No Access`: Can't take actions

All administrators also have the ability to manage the users that they are supervisors for.