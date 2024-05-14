from flask import Flask, render_template,  request, url_for, flash, redirect, make_response
import csv
import random
import datetime
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a24b722b440cc959b6db422125aed818acdcbcd3a22a6af2'
socketio = SocketIO(app)


def write_person_to_csv(data, rand_id, current_time):
    with open('people.csv', mode='a', newline='') as database:
        first_name = data['first_name']
        last_name = data['last_name']
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([rand_id, first_name, last_name])
    database.close()

def write_entry_to_csv(rand_id, current_time, dependants):
    with open('database.csv', mode='a', newline='') as database:
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([rand_id, current_time, False, dependants])
    database.close()

def check_signed_in(rand_id):
    
        #check if there is an open session from another date and close it
    with open('database.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        rows = list(csv_reader)
        for row in rows:
            if row[0] == rand_id and row[2] == 'False':
                if datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f').date() != datetime.datetime.now().date():
                    #set signout to sign in date 18:00:00
                    mod = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f').replace(hour=18, minute=0, second=0, microsecond=0)
                    row[2] = datetime.datetime.strftime(mod, '%Y-%m-%d %H:%M:%S.%f')
                break
    with open('database.csv', mode='w', newline='') as database:
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(rows)
    
    with open('database.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        for row in csv_reader:
            #print(row[0] == rand_id, row[4] == 'False')
            if row[0] == rand_id and row[2] == 'False':
                return True
    return False

def check_user_exists(rand_id):
    with open('people.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        for row in csv_reader:
            if row[0] == rand_id:
                return True
    return False

def get_user_name(rand_id):
    with open('people.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        for row in csv_reader:
            if row[0] == rand_id:
                return [row[1], row[2]]
    return None

def write_to_machine_use(machine_id, rand_id):
    usage_id = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
    with open('machine_usage.csv', mode='a', newline='') as database:
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #usage_id, machine_id, user_id, start_time, start_time+1 hour
        csv_writer.writerow([usage_id, machine_id, rand_id, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(hours=1)])
    database.close()
    return usage_id

def checkout_machine_use(usage_id):
    #update machine_usage.csv, last row to current time
    with open('machine_usage.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        rows = list(csv_reader)
        for row in rows:
            if row[0] == usage_id:
                row[4] = datetime.datetime.now()
                break
    with open('machine_usage.csv', mode='w', newline='') as database:
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(rows)

@app.route('/')
def index():
    rand_id = request.cookies.get('uuid')
    if rand_id:
        if check_signed_in(rand_id):
            return render_template('signout.html')
        elif check_user_exists(rand_id):
            names = get_user_name(rand_id)
            return render_template('index.html', names=names)
        else:
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/signin', methods=['POST'])
def signin():
    rand_id = request.cookies.get('uuid')    
    if check_user_exists(rand_id):
        #check if they changes their name
        data = request.form.to_dict()
        names = get_user_name(rand_id)
        if names[0] != data['first_name'] or names[1] != data['last_name']:
            if data['first_name'] == '':
                return render_template('index.html', error='first_name', names=names)
            if data['last_name'] == '':
                return render_template('index.html', error='last_name', names=names)
            #update people.csv
            with open('people.csv', mode='r') as database:
                csv_reader = csv.reader(database)
                rows = list(csv_reader)
                for row in rows:
                    if row[0] == rand_id:
                        row[1] = data['first_name']
                        row[2] = data['last_name']
                        break
            with open('people.csv', mode='w', newline='') as database:
                csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerows(rows)
        #create entry in database.csv
        current_time = datetime.datetime.now()
        print(data)
        write_entry_to_csv(rand_id, current_time, data['dependants'])
        response = make_response(render_template('success.html'))
        response.set_cookie('uuid', rand_id, max_age=datetime.timedelta(days=400))
        return response
    else:
        #create entry in people.csv
        data = request.form.to_dict()
        current_time = datetime.datetime.now()
        
        if data['first_name'] == '':
            return render_template('index.html', error='first_name')
        if data['last_name'] == '':
            return render_template('index.html', error='last_name')
        
        rand_id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        write_person_to_csv(data, rand_id, current_time)
        #create entry in database.csv
        write_entry_to_csv(rand_id, current_time, data['dependants'])
        #set cookie
        response = make_response(render_template('success.html'))
        response.set_cookie('uuid', rand_id, max_age=datetime.timedelta(days=400))
        return response

@app.route('/signout', methods=['POST'])
def signout():
    rand_id = request.cookies.get('uuid')
    #update database.csv
    with open('database.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        rows = list(csv_reader)
        for row in rows:
            if row[0] == rand_id and row[2] == 'False':
                row[2] = datetime.datetime.now()
                break
    with open('database.csv', mode='w', newline='') as database:
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(rows)
    return 'You have been signed out. You can now close your browser.'


@app.route('/machine_use', methods=['GET', 'POST'])
def machine_use():
    if request.method == 'POST':
        form = request.form.to_dict()
        rand_id = request.cookies.get('uuid')

        if check_signed_in(rand_id):
            usage_id = write_to_machine_use(form['machine_id'], rand_id)
            response = make_response(render_template('machine_use.html', usage_id=usage_id))
            response.set_cookie('usage_id', usage_id, max_age=datetime.timedelta(days=400))
            return render_template('machine_use.html')
        else:
            return redirect(url_for('index'))

@app.route('/get_logged_in', methods=['GET'])
def get_logged_in():
    sign_out_old()
    people = {}
    with open('people.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        for row in csv_reader:
            people[row[0]] = [row[1], row[2]]
    
    open_sessions = []
    with open('database.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        for row in csv_reader:
            if row[2] == 'False' or datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f').date() == datetime.datetime.now().date():
                open_sessions.append(row)

    sessions = []
    for session in open_sessions:
        session = {
            'first_name': people[session[0]][0],
            'last_name': people[session[0]][1],
            'start_time': session[1],
            'end_time': session[2]
        }
        sessions.append(session)


    return render_template('sessions.html', sessions=sessions)

def get_deople_dict():
    people = {}
    with open('people.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        for row in csv_reader:
            people[row[0]] = [row[1], row[2]]
    return people

def check_user_in_list(user, list):
    for item in list:
        if item['user'] == user:
            return True
    return False

@app.route('/get_user_numbers/<date>', methods=['GET'])
def get_user_numbers(date):
    sign_out_old()
#Loop through csv and count unique users on a given date and add the number of dependants [3] of each user to the count
    numbers = []
    
    people = get_deople_dict()
    
    with open('database.csv', 'r') as file:
        #loop thorugh lines
        for line in file:
            #split the line by comma
            line = line.split(',')
            #6314A651E1E4DA0F,2024-03-23 10:32:31.247358,2024-03-23 18:00:00.000000,0
            line_date = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f')
            search_date = datetime.datetime.strptime(date, '%Y-%m-%d')
            
            if line_date.date() == search_date.date():
                if check_user_in_list(people[line[0]], numbers):
                    pass
                else:
                    numbers.append(
                        {
                            'user': people[line[0]],
                            'dependants': int(line[3]),
                            'time_in': line[1],
                            'time_out': line[2]
                        }
                    )
                        

        total = 0
        
        for number in numbers:
            total += number['dependants'] + 1
                
    return render_template('date_sessions.html', sessions=numbers, total_numbers=total)

@app.route('/add_manual_user', methods=['GET', 'POST'])
def add_manual_user():
    if request.method == 'POST':
        data = request.form.to_dict()
        rand_id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        write_person_to_csv(data, rand_id, datetime.datetime.now())
        
        today_date_six = datetime.datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
        #add signout at 18:00
        with open('database.csv', mode='a', newline='') as database:
            csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([rand_id, datetime.datetime.now(), today_date_six.strftime("%Y-%m-%d %H:%M:%S.%f"), data['dependants']])
        
        return render_template('success.html')
    return render_template('add_manual_user.html')


def sign_out_old():
    with open('database.csv', mode='r') as database:
        csv_reader = csv.reader(database)
        rows = list(csv_reader)
        for row in rows:
            if row[2] == 'False':
                if datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f').date() != datetime.datetime.now().date():
                    #set signout to sign in date 18:00:00
                    mod = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f').replace(hour=18, minute=0, second=0, microsecond=0)
                    row[2] = datetime.datetime.strftime(mod, '%Y-%m-%d %H:%M:%S.%f')
        with open('database.csv', mode='w', newline='') as database:
            csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(rows)
    return True

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001 )