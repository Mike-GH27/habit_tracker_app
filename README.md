# Habit Tracker App

## Description
The habit tracker application enables the user to track their habits und analyze their performance. The application is accessed via console command and uses a CLI.

## Installation
Copy the directory to your computer and navigate to the directory:

* make sure to have python installed at least version 3.12 and the following packages:
  * pandas 2.0.3
  * sqlalchemy 2.0.23
  * click 8.1.7
* or alternatively enter "pip install -r requirements.txt" into the console while having your environment activated and being in application directory

## Usage
While in the directory start the application by starting the menu.py file. Type into your console
* python menu.py (Windows)
* python3 menu.py (Linux/Mac)

The CLI is mostly navigated by entering the menu item numbers into the console. For example, you enter "5" into the console in the main menu to save and exist the application.

## Test data
To try out the functionality, test data is provided in the tracker_testing_data.py file. Running the file will create
a save file called "user_data.db", which will be automatically loaded upon starting the application. Note: running the file will replace the
current save file, so make sure to backup your user data before running the script.

To remove the test data, just delete "user_data_db" in the main directory.

To setup the test data type into the console the following (while being in the main directory):
* python tracker_testing_data.py (Windows)
* python3 tracker_testing_data.py (Linux/Mac)

## Unit Test
A unit test is provided to check the core functionality of the application. To run the unit test:
* go to the main directory with your console
* "cd unit_test" to go to the subdirectory
* "python tracker_test_suite" (python3 on Linux/Mac) to start the test_suite



