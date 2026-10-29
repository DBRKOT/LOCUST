from faker import Faker
from locust import HttpUser, task, SequentialTaskSet, TaskSet, constant_throughput
import random

fake = Faker('ru_Ru')
# print(fake.address())

class AdminTests(TaskSet):
    def on_start(self):
        self.client.get('/login/')
        self.client.post('/login/', data={
            'username': 'reception',
            'password' : 'fitness123',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken')
        }, headers={
            'Referer': self.client.base_url + '/login/'
        })

    @task(15)
    def search_clients(self):
        self.client.get('/clients/?q=' + fake.last_name())

    @task(15)
    def open_schedule(self):
        self.client.get('/schedule/' + str(random.choice([1, 2, 3, 4, 5])) + '/')

    @task(1)
    def add_client(self):
        self.client.get('/clients/new/')
        client_data = {
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken'),
            'full_name': fake.last_name() + ' ' + fake.first_name() + ' ' + fake.middle_name(),
            'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=60).isoformat(),
            'gender': random.choice(['М', 'Ж']),
            'phone': fake.numerify('+7 (9##) ###-##-##'),
            'email': fake.email(),
            'address': fake.address().replace('\n', ', '),
            'contraindications': random.choice(['нет', 'астма', 'проблемы со спиной']),
            'source': random.choice(['сайт', 'реклама', 'друзья', 'соцсети'])
        }
        self.client.post('/clients/new/', data=client_data, headers={
            'Referer': self.client.base_url + '/clients/new/'
        })

    @task(1)
    def add_payment(self):
        self.client.get('/payments/new/')
        payment_data = {
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken'),
            'client': str(random.randint(1, 8)),
            'subscription': '',
            'personal_training': '',
            'amount': str(fake.random_int(min=1500, max=12000)),
            'payment_date': fake.date_time_this_month().strftime('%Y-%m-%dT%H:%M'),
            'payment_type': random.choice(['абонемент', 'персональная тренировка', 'дополнительная услуга']),
            'payment_method': random.choice(['наличные', 'карта', 'онлайн']),
            'status': 'оплачено'
        }
        self.client.post('/payments/new/', data=payment_data, headers={
            'Referer': self.client.base_url + '/payments/new/'
        })

    @task(1)
    def enroll_client(self):
        schedule_id = str(random.choice([1, 2, 3, 4, 5]))
        self.client.get('/schedule/' + schedule_id + '/')
        enroll_data = {
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken'),
            'client': str(random.randint(1, 8))
        }
        self.client.post('/schedule/' + schedule_id + '/enroll/', data=enroll_data, headers={
            'Referer': self.client.base_url + '/schedule/' + schedule_id + '/'
        })

class NewClientFlow(SequentialTaskSet):
    def on_start(self):
        self.client.get('/login/')
        self.client.post('/login/', data={
            'username': 'reception',
            'password' : 'fitness123',
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken')
        }, headers={
            'Referer': self.client.base_url + '/login/'
        })

    @task
    def open_form(self):
        self.client.get('/clients/new/')

    @task
    def save_client(self):
        client_data = {
            'csrfmiddlewaretoken': self.client.cookies.get('csrftoken'),
            'full_name': fake.last_name_female() + ' ' + fake.first_name_female() + ' ' + fake.middle_name_female(),
            'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=60).isoformat(),
            'gender': 'Ж',
            'phone': fake.numerify('+7 (9##) ###-##-##'),
            'email': fake.email(),
            'address': fake.address().replace('\n', ', '),
            'contraindications': 'нет',
            'source': random.choice(['сайт', 'реклама', 'друзья'])
        }
        self.client.post('/clients/new/', data=client_data, headers={
            'Referer': self.client.base_url + '/clients/new/'
        })

class websiteUser(HttpUser):
    wait_time = constant_throughput(2)
    tasks = [
        AdminTests,
        NewClientFlow
    ]