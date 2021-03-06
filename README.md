[![Build Status](https://travis-ci.org/gnosis/gnosisdb.svg?branch=master)](https://travis-ci.org/gnosis/gnosisdb)
[![Coverage Status](https://coveralls.io/repos/github/gnosis/gnosisdb/badge.svg?branch=master)](https://coveralls.io/github/gnosis/gnosisdb?branch=master)
![Python 3.6](https://img.shields.io/badge/Python-3.6-blue.svg)
![Django 2](https://img.shields.io/badge/Django-2-blue.svg)

# GnosisDB
Gnosis Core Database Layer

Installation
-------

### Install Docker and Docker Compose
* First, install docker: https://docs.docker.com/engine/installation/.
* Then, install docker compose: https://docs.docker.com/compose/install/
* Clone the repository and change your working directory:

```
git clone https://github.com/gnosis/gnosisdb.git
cd gnosisdb
```

### Build containers
The application is made up of several container images that are linked together using docker-compose. Before running the application, build the images:

`docker-compose build --force-rm`

### Create a Django superuser
Run the Web container with the following command and inside create a super user in order to access the /admin interface.

```
docker-compose run web bash
python manage.py migrate
python manage.py createsuperuser
```

### Run application
Start the gnosisdb server simply by bringing up the set of containers:

`sudo docker-compose up`

You can access it on http://localhost:8000 and the admin is on http://localhost:8000/admin

### Populate database
To populate database and retrieve some information, the easiest is to use [gnosis.js](https://github.com/gnosis/gnosis.js)
with a local blockchain (Ganache-cli).

[Gnosis.js](https://github.com/gnosis/gnosis.js) will deploy gnosis smart contracts and run some operations between them (emulates the creation of oracles, events and markets),
so you will have information in your private blockchain for gnosisdb to index.

```
git clone https://github.com/gnosis/gnosis.js.git
cd gnosis.js
npm install
```

You will need to have Ganache-cli running, which has been downloaded by previous `npm install`. So in the same gnosis.js folder:

`./node_modules/.bin/ganache-cli --gasLimit 40000000 -d -h 0.0.0.0 -i 437894314312`

The -d option allows you to get the same address everytime a contract is deployed. You will not have to update your django settings everytime a new Ganache server is running.

The -h option tells Ganache to listen on all interfaces, including the bridge interfaces which are exposed inside of the docker containers.
This will allow a setting of `ETHEREUM_NODE_HOST = '172.x.x.x'` to work for the Celery worker.

The -i option sets the network id.

Open another window and go to the gnosis.js folder, deploy the contracts and run gnosisdb tests. This emulates the creation of oracles, events and markets.
Docker containers must be up because *tests require ipfs, and* of course *Ganache-cli* too:

```
npm run migrate
npm run test-gnosisdb
```

The execution will furnish all the contracts' addesses in the `node_modules/@gnosis.pm/gnosis-core-contracts/build/contracts` folder as parts of the build artifacts.
You should also see the addresses displayed in your console.

You should verify that the addresses in ETH_EVENTS specified in gnosisdb/settings/base.py match what is displayed by the console for all the contracts including:

* Centralized Oracle Factory
* Event Factory
* Standard Market Factory

Open your browser and go to http://localhost:8000/admin, provide your superuser username and password.
You should now see something like this:

![Admin overview](https://github.com/gnosis/gnosisdb/blob/master/img/django_admin_overview.png)

Create now a Celery periodic task. This _Event Listener_ task will start indexing and processing information in the blockchain.

![Periodic task management](https://github.com/gnosis/gnosisdb/blob/master/img/django_celery.png)


### Development
Every time you do a change in the source code run `docker-compose build` to apply the code changes and
then `docker-compose up` to get GNOSISDB up and running.


Django Settings
-------

GnosisDB comes with a production settings file that you can edit.

##### ALLOWED_HOSTS
Specify the list of allowed hosts to connect to GnosisDB:

`ALLOWED_HOSTS = ['.gnosis.pm', '127.0.0.1', 'localhost']`

##### ADMINS
Specify your application administrators:

```
ADMINS = (
    ('Batman', 'batman@gnosis.pm'),
    ('Robin', 'robin@gnosis.pm'),
)
```

##### ETHEREUM
Provide an Ethereum _host_, _port_ and _SSL (0, 1)_. Use _SSL = 1_ only if your Ethereum host supports HTTPS/SSL.
Communication with node will use **RPC through HTTP/S**

```
ETHEREUM_NODE_HOST = os.environ['ETHEREUM_NODE_HOST']
ETHEREUM_NODE_PORT = os.environ['ETHEREUM_NODE_PORT']
ETHEREUM_NODE_SSL = bool(int(os.environ['ETHEREUM_NODE_SSL']))
```

You can also provide an **IPC path** to a node running locally, which will be faster.
You can use the environment variable  _ETHEREUM_IPC_PATH_.
If set, it will override _ETHEREUM_NODE_HOST_ and _ETHEREUM_NODE_PORT_, so **IPC will
be used instead of RPC**:

```
ETHEREUM_IPC_PATH = os.environ['ETHEREUM_IPC_PATH']
```

Number of concurrent threads connected to the ethereum node can be configured:

```
ETHEREUM_MAX_WORKERS = os.environ['ETHEREUM_MAX_WORKERS']
```

##### IPFS
Provide an IPFS host and port:

```
IPFS_HOST = os.environ['IPFS_HOST']
IPFS_PORT = os.environ['IPFS_PORT']
```

##### RABBIT MQ
RabbitMQ is the default Celery's messaging broker, other brokers are Redis and Amazon SQS.<br/>
More info about Celery's brokers at [this link](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html).<br/>
If you're willing to run RabbitMQ in a Dokku/Docker container, please read out [this link](https://github.com/dokku/dokku-rabbitmq).

```
RABBIT_HOSTNAME = os.environ['RABBIT_HOSTNAME']
RABBIT_USER = os.environ['RABBIT_USER']
RABBIT_PASSWORD = os.environ['RABBIT_PASSWORD']
RABBIT_PORT = os.environ['RABBIT_PORT']
RABBIT_QUEUE = os.environ['RABBIT_QUEUE']
BROKER_URL = 'amqp://{user}:{password}@{hostname}:{port}/{queue}'.format(
    user=RABBIT_USER,
    password=RABBIT_PASSWORD,
    hostname=RABBIT_HOSTNAME,
    port=RABBIT_PORT,
    queue=RABBIT_QUEUE
)
```
##### LMSR MARKET MAKER
You need to specify the LMSR Market Maker address you have deployed previously (to discover how to do that please take a look at [gnosis-contracts](https://github.com/gnosis/gnosis-contracts):

`LSRM_MARKET_MAKER = '2f2be9db638cb31d4143cbc1525b0e104f7ed597'`

##### GNOSIS ETHEREUM CONTRACTS
The ETH_EVENTS array variable allows you to define and map a list of addressess to their related event listeners.<br/>
Create a new array variable in your settings file and call it ETH_EVENTS as follows:

```
ETH_EVENTS = [
    {
        'ADDRESSES': ['254dffcd3277c0b1660f6d42efbb754edababc2b'],
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'yourmodule.event_receivers.YourReceiverClass',
        'NAME': 'Your Contract Name',
        'PUBLISH': True,
    },
    {
        'ADDRESSES_GETTER': 'yourmodule.address_getters.YouCustomAddressGetter',
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketInstanceReceiver',
        'NAME': 'Standard Markets Buy/Sell/Short Receiver'
    }
]
```
Please read out the "How to implement your own AddressGetter and EventReceiver" paragraph for a deeper explication on how to develop your listeners.

How to implement your own AddressGetter and EventReceiver
-------
Let's consider the ETH_EVENTS settings varable:
```
ETH_EVENTS = [
    {
        'ADDRESSES': ['254dffcd3277c0b1660f6d42efbb754edababc2b'],
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'yourmodule.event_receivers.YourReceiverClass',
        'NAME': 'Your Contract Name',
        'PUBLISH': True,
    },
    {
        'ADDRESSES_GETTER': 'yourmodule.address_getters.YouCustomAddressGetter',
        'EVENT_ABI': '... ABI ...',
        'EVENT_DATA_RECEIVER': 'chainevents.event_receivers.MarketInstanceReceiver',
        'NAME': 'Standard Markets Buy/Sell/Short Receiver'
    }
]
```
As you can see, the properties that come into play are:
* ADDRESSES, the list of contract's addresses you may want to watch and listen to
* EVENT_ABI, the contract's JSON ABI in string format
* EVENT_DATA_RECEIVER, a custom event data receiver class
* NAME, the contract name
* PUBLISH, it denotes that this part of the config should have the addresses field in it published on that REST endpoint (see REST API paragraph)
* ADDRESSES_GETTER, a custom addresses getter class

##### EVENT DATA RECEIVER
An Event Data Receiver is responsible for storing data into a database.<br/>
All the receivers must inherit from [**django_eth_events.chainevents.AbstractEventReceiver**](https://github.com/gnosis/django-eth-events/blob/master/django_eth_events/chainevents.py#L16) class and implement the **save(self, decoded_event, block_info)** method.

Below the CentralizedOracleFactoryReceiver. It instantiates the CentralizedOracleSerializer, then verify if input data is valid, and finally save everything into the database.

```
from django_eth_events.chainevents import AbstractEventReceiver


class CentralizedOracleFactoryReceiver(AbstractEventReceiver):

    def save(self, decoded_event, block_info):
        serializer = CentralizedOracleSerializer(data=decoded_event, block=block_info)
        if serializer.is_valid():
            serializer.save()
            logger.info('Centralized Oracle Factory Result Added: {}'.format(dumps(decoded_event)))
        else:
            logger.warning(serializer.errors)
```

##### ADDRESSES GETTER
In case you wouldn't directly declare the contract address/addresses, you should specify an Addresses Getter class instead.<br/>
An Addresses Getter class must inherit from [**django_eth_events.chainevents.AbstractAddressesGetter**](https://github.com/gnosis/django-eth-events/blob/master/django_eth_events/chainevents.py#L5) and implement two methods:
* get_addresses(self), returns a list of strings (addresses)
* __contains__(self, address), returns True if the given address is in the addresses list, False otherwise

Take a look at ContractAddressGetter:

```
from gnosisdb.relationaldb.models import Contract
from django.core.exceptions import ObjectDoesNotExist
from django_eth_events.chainevents import AbstractAddressesGetter


class ContractAddressGetter(AbstractAddressesGetter):
    """
    Returns the addresses used by event listener in order to filter logs triggered by Contract Instances
    """
    class Meta:
        model = Contract

    def get_addresses(self):
        """
        Returns list of ethereum addresses
        :return: [address]
        """
        return list(self.Meta.model.objects.values_list('address', flat=True))

    def __contains__(self, address):
        """
        Checks if address is contained on the Contract collection
        :param address: ethereum address string
        :return: Boolean
        """
        try:
            self.Meta.model.objects.get(address=address)
            return True
        except ObjectDoesNotExist:
            return False
```

REST API
-------
GnosisDB comes with a handy RESTful API. Run GnosisDB, open your Web browser and connect to http://localhost:8000. You will get all the relevant API endpoints and their input/return data.

RESYNC DATABASE
----------------
To resync database with the blockchain, first we must delete every information that is on the database with the following task:

`python manage.py cleandatabase`

Then we must force the daemon to resync everything again:

`python manage.py resync_daemon`


BACKUP DATABASE
----------------
If you use `python manage.py db_dump` you will get a backup of the database on the mail (it will be generated in _/tmp_ folder of the machine),
using custom Postgres format (as recommended on the docs). If you want to convert it to standard SQL:

`pg_restore -f mydatabase.sqlc mydatabase.dump`


GNOSISDB DEPLOYMENT IN KUBERNETES
----------------------------------

### Requirements

There are a few necessary requirements:
  - Minimum Kubernetes version:  **1.9**
  - Ethereum network: **Rinkeby** (in the example)  
    - If you want another network you must change the address:
      - Download https://github.com/gnosis/gnosis-contracts
      - Execute `truffle networks`
      - Replace the example addresses with this new ones in `gnosisdb-web-deployment.yaml`, `gnosisdb-worker-deployment.yaml` and `gnosisdb-scheduler-deployment.yaml` files

### Database
   ##### Database creation
   It is necessary to create a database so that GnosisDB could index blockchain events.

   GnosisDB is tested with **Postgres** database, if you want to use another database you will have to change the connection driver.
   ##### Database secret creation
   Set your database params.
  ```
  kubectl create secret generic gnosisdb-database \
  --from-literal host='[DATABASE_HOST]' \
  --from-literal name=[DATABASE_NAME] \
  --from-literal user=[DATABASE_USER] \
  --from-literal password='[DATABASE_PASSWORD]' \
  --from-literal port=[DATABASE_PORT]
  ```

### Persistent volume creation
It will be used for storing blockchain data of Geth node.

### Rabbit service
It is necessary for sending messages between gnosisdb scheduler and worker. Run rabbit service:

  ```
  kubectl apply -f rabbitmq-gnosisdb
  ```

### Gnosisdb services
##### Web
Set your custom environment variables in `gnosisdb-web-deployment.yaml`. You **only** have to set environment variables which have the `# CUSTOM` annotation.

##### Celery Scheduler
Set your custom environment variables in `gnosisdb-scheduler-deployment.yaml`. You **only** have to set environment variables which have the `# CUSTOM` annotation.

##### Celery Worker
  - Set your custom environment variables in `gnosisdb-worker-deployment.yaml`. You **only** have to set environment variables which have the `# CUSTOM` annotation.
  - Set persistent volume which was created in a previous step. Geth node uses it.

##### RUN services
After setting custom environments in the previous steps, application can be started. Apply to the folder `gnosisdb` the following command:
```
kubectl apply -f gnosisdb
```

### Celery task configuration
  - Create an admin user to access the /admin interface.
  ```
    kubectl exec -it [GNOSISDB_WEB_POD_NAME] -c web bash
    python manage.py createsuperuser
  ```
  - Login into the admin /interface with your admin user
  - Create celery periodic task (follow the paragraph where It is explained).


Contributors
------------
- Stefan George (stefan@gnosis.pm)
- Denís Graña (denis@gnosis.pm)
- Giacomo Licari (giacomo.licari@gnosis.pm)
- Uxío Fuentefría (uxio@gnosis.pm)
