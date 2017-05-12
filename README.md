# Publishing Database: Lab 2 CS 61

## How to Run:

* type "python db.py" into shell

* All commands are taken through stdin

## Specifications:

* First you will be prompted for a master key for accessing passwords in the database, this will need to be remembered as well as the password for each user.

* Then users will be prompted for there role in the publishing company followed by their unique id/password or they will be prompted to register if this is their first time using the database.

* Once the user has been authenticated, each of the different roles in the company have access to separate parts of the database

* Authors may view the status of their manuscripts, submit manuscripts or remove their manuscripts from the system

* Editors may check the status of their assigned manuscripts, assign manuscripts, reject manuscripts, accept manuscripts, accept manuscripts, typeset manuscripts, schedule manuscripts or publish manuscripts

* Reviewers can see only the manuscripts that they are reviewing and can score only manuscripts that are under review and assigned to them, otherwise an error message is displayed to the user.

## Extra Credit:

* Part 1: Registration does safely collect passwords in our program, and takes a master key as specified

* Transactions are only accepted when the user is authorized

* Part 2: Since our users already essentially have separate interfaces assigned by role using the GRANT on the table level is not necessary. Users only have access to commands because of their role, and we have ensured that resigned reviewers can no longer login, even though their data is retained.
