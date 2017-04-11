# Item Catalog Project 

## Introduction

Provided design brief: "You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items."

Because the categories and items were not specifically defined, I decided to build something that may be useful to me. This landed up being a collection of various marketing tactics and the general strategies under which they fall. 

While the presentation of tactics and strategies is currently very basic, I would like to add some more robustness in the future by adding content to each of the tactics so users can go through their implementation step-by-step on the site – rather than clicking through to an outside resource. A strategy or tactic picker of sorts that finds tactics based on budget/difficulty/time required would also be a nice future addition. 

## Requirements

> The project was designed to meet the following requirements as part of Udacity's Full-Stack Nanodegree Program:

- The project implements a JSON endpoint that serves the same information as displayed in the HTML endpoints for an arbitrary item in the catalog.
- Website reads category and item information from a database.
- Website includes a form allowing users to add new items and correctly processes submitted forms.
- Website does include a form to edit/update a current record in the database table and correctly processes submitted forms.
- Website does include a function to delete a current record.
- Create, delete and update operations do consider authorization status prior to execution.
- Page implements a third-party authentication & authorization service (like Google Accounts or Mozilla Persona) instead of implementing its own, insecure authentication & authorization spec.
- Make sure there is a 'Login' and 'Logout' button/link in the project. The aesthetics of this button/link is up to the discretion of the student.
- Code is ready for personal review and neatly formatted.
- Comments are present and effectively explain longer code procedures.
- README file includes details of all the steps required to successfully run the application.


## Installation

Pre-reqs: 
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

1. Launch the Vagrant VM (`vagrant up`)
2. `cd` to marketing_catalog 
3. Run `python database_setup.py` to setup the db
4. Run `python populate_db.py` to add some initial data to the db
5. Run `python project.py` to start the local server
6. Access and test your application by visiting `http://localhost:5000` locally

Alternatively, a live version of this app can be found at https://agile-river-74734.herokuapp.com/ 

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [SQLAlchemy](https://www.sqlalchemy.org/) - SQL Toolkit and ORM
* [Twitter OAuth](https://dev.twitter.com/oauth) - User aunthentication

## License

This project is licensed under the MIT License.