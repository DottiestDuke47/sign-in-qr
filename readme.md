# Simple QR sign in app
## Written with Flask, HTMX and Bootstrap.

### Instructions:
- Install python and flask
- Create database.csv and people.csv in root next to main.py
- run the main.py file

### How it works:
- When someone visits the page for the first time, they fill in thier name, which is then:
	- Stored in the people.csv. 
	- An entry is created in database.csv when they sign in.
	- a cookie is created in the users browser with a uuid
- If someone is already signed in, they get presented with a sign out button, which updates database.csv with the sign-out time.
- if someone had visited before, thier name will be pre-polulated, which is possible because of the cookie.