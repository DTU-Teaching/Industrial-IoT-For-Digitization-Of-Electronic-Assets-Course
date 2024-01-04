# Setting up the cloud and connecting a IoT device

Some general information relevant for this exercise:
- Azure Resource groups: grouping of multiple resources for organization.
- Most selections can be left on the default.

## IoT Hub

Create an IoT hub on Azure following this tutorial and register a demo device (the "Update the IoT hub" can be skipped): https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-create-through-portal

Use the IoT Hub free tier.

## Create as sample device on your laptop

Create a simulated device running on your laptop similar to this example and run it. https://github.com/Azure/azure-iot-sdk-python/blob/main/samples/async-hub-scenarios/send_message.py
You just have to insert your connection string found on device properties found on the IoT Hub.

Using the IoT hub VSCode extension you can start monitoring the build in event endpoint and check that your messages are received by the IoT Hub. You have to make sure you are logged in to Azure in VSCode. The extension page shows how to monitor the endpoint: https://marketplace.visualstudio.com/items?itemName=vsciot-vscode.azure-iot-toolkit

## Connect the RevPi as a IoT device to the IoT Hub

Using the setup from yesterday connect the RevPi to the IoT Hub and send messages with all the values read from the PLC. Additionally record the time of measuring.
For example you can read the values of the plc every second and send the data to the IoT hub every 20 seconds (this avoids hitting the daily message limit of 8000 of the free tier). Make sure you are sending the data in a format that can easily be used for further processing like json.

Again check that the messages are received by the IoT Hub.

## Create a Database

We are now receiving message on the IoT Hub and they are only stored temporarily until they are processed for up to 24 hours, so to store them permanently we need some kind of storage.
We are going to utilize a PostgreSQL database to store the recorded values. (We skip the timescaleDB extension in this example for simplicity, you are free to explore and use it on your own)

Follow this tutorial to create a flexible postgres server on Azure: 
https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/quickstart-create-server-portal

You can choose Development for the workload type and under the network add you current ip as allowed for the firewall.
If you access the server later from a different location you need to allow that ip again on the networking page for the server on Azure (This can also be necessary if you public ip changes at the same location). Here check the box "Allow public access from any Azure service within Azure to this server" as well to be able to access the server from the Azure function later.

### Connect with pgAdmin to the database
On the left panel right click on Servers>register>Server...
Give the server a name to display and the under Connection enter the Host name (found on the Azure dashboard) and user and password. The remaining values can be left on the default.

#### Create a table
Then you can create a table on the server
![](imgs/pgadmin_create_table.png)
Give the table a name and add columns for all the values you want to store. For the datatype you can use double precision for floating point numbers, bigint for integers and character varying for strings. Further can timestamp with time zone be used to store time information.

Set the time of measurement as a primary key, this means it can be used to uniquely identify each entry in the table. As a side effect this value has to be present for each row and no duplicates can exist.

On the last tab of the table creation you can see the SQL that will be executed to create the table.

By right clicking on the table you can view the data. Right now it is empty but late you can use it verify that the data arrives in the database.

# Storing the data in a database

We have now connected the IoT device to the cloud via the IoT hub and we have created a place where we can store the data.
Now we need to connect these two parts.

## Preparation

#### Enabling Resource provider

Under your Subscription on Azure select Resource providers and search for microsoft.eventgrid, then register it.
![](imgs/enable_eventgrid.png)

#### Create User for the Azure function

For security reasons we are creating a separate user with credentials and minimal permissions.
Using pgAdmin by right clicking on the Login/Group Roles create a new Login/Group role...
Enter a name as username in the General tab and set a password on the definition tab, additional enable Can login? on the Privileges tab. Now save the user.

By default the user has no rights, so to enable the user to write to the database where we store the data the appropriate rights have to be granted.
To do that right click on the Tables (as [shown](#create-a-table)) and select "Grant Wizard...". Then in the first step select the table and in the next step add the previously created user a Grantee and add "insert" as privileges. Save the privileges by clicking finish on the review screen. With this setup the newly created user is only allowed to add data to the database. Use this user when working with the azure function.

## Creating a function app

Create a Function app on azure.

Select:
- Python Version 3.11
- Linux
- Consumption plan

### Creating a function

#### Setup
Open VSCode in a new folder to create a Azure function project.
In VSCode press CTRL+Shift+P to open the command palate. Search and select Azure Functions: Create Function.
Select a folder (most likely the current new folder for the project), select python as a function programming language with model V2.
After selecting a python interpreter use EventGrid trigger for the activation of the function.

A few notes on the project.
- The requirements.txt specifies the packages needed by the function and which are installed in the cloud (you need to specify this separately from what you are using in the conda environment)
- for psycopg2 use "psycopg2-binary" since the normal version does not work with azure functions
- In local.settings.json you can specify environment variables. Use these to avoid putting your credentials in your code!: 
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "DB_USER": "user", // example for user
    "DB_PASSWORD": "password" // example for password
  }
}
```
- psycopg2 has to be imported in the function definition and not at the top of the file (Azure function specific issue)

#### Coding 

This is an example for getting the message from the event:
```python
@app.event_grid_trigger(arg_name="event")
def hubtodbfunction(event: func.EventGridEvent):

    event_dict = event.get_json()

    message = event_dict["body"] # deserialized message sent from the IoT device
    device_id = event_dict["systemProperties"]["iothub-connection-device-id"] # example of one of the properties attached to the message see for full details: https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-event-grid#device-telemetry-schema
```

This is an example of how to insert values into the database. You have to adapt the example to fit your values and setup. Keep in mind that depending how you followed the previous step you have to insert multiple rows of data.

```python
## accessing variable previously set in the local.setting.json
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_connection = "<whateverdatabase>.postgres.database.azure.com:5432/postgres?sslmode=require"

CONNECTION = f"postgres://{username}:{password}@{db_connection}"
import psycopg2 
with psycopg2.connect(CONNECTION) as conn:
	cur = conn.cursor()

	sql_str = "INSERT INTO <table name> ( time, pump1_speed, pump2_speed, <other colums> ) VALUES ( %s, %s, %s, <repeat for the number of columns> )"
	cur.execute(sql_str, (message["time"], message["pump1_speed"], message["pump2_speed"], <other values>))
		
	conn.commit()
```

With the examples given and the template created, write a complete function that retrieves the data from the message send by the devices and store all values in the database.

#### Running the function locally

To run the function locally first you have to start all three Azurite services by clicking on them at the bottom of your VSCode window.

[<img src="imgs/azurite.png" width="300"/>]()

Then you can press F5 to start the local Azure function environment. After the setup is completed you can run the function locally from the azure tab on the left.

[<img src="imgs/azure_fun_local.png" width="300"/>]()

As payload you can adapt the body of this example to match your message, just exclude the outer square brackets: https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-event-grid#device-telemetry-schema

Using pgadmin you can check if the data was stored in the database.

#### Deploying the function in the cloud

After successfully testing the function locally you can deploy the function to your previously created function app.

[<img src="imgs/azure_fun_deploy.png" width="300"/>]()

Additionally you have to push the environment variable specified in the local.setting.json to the cloud. This can be done by executing "Azure Functions: Upload local settings" from the command palette.

Check on the Azure portal if the function is deployed.

If you click on the Function inside the function app you can see the code and monitor the function, either see past executions or stream the output live.
However the function is not executed yet, because the data from the IoT Hub is not forwarded yet.

### Connecting the Azure function to the IoT Hub

In the IoT Hub you have to create a EventGrid subscription to forward the events to the azure function.

![](imgs/create_event.png)

For Event types only select device telemetry and select your just deployed azure function.

If your device is running and sending telemetry messages they should appear in the database with a slight delay.

If not check the different parts of the chain to investigate what causes errors. This can also be helpful if everything works to get familiar with the setup.

# Retrieving the data from the database
From python you can query the table and create a pandas dataframe like this:

```python
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
CONNECTION = f"postgres://{username}:{password}@<your database name>.postgres.database.azure.com:5432/postgres?sslmode=require"

with psycopg2.connect(CONNECTION) as conn:
	data_raw = pd.read_sql("SELECT * from <table name>;", conn)
```

By modifying the SQL query you can limit he dataframe for example in time range or columns retrieved.

# Grafana

## Installing Grafana in Azure

Search for "Azure Managed Grafana" and create a instance. For pricing plan the standard provides a fee instance for the first 30 days and don't forget to add yourself as an administrator on the permissions tab.
After the resource is created you can find the endpoint to access the dashboard on the overview of the resource. You can login with the same account as used for the Azure portal.

## Adding a datasource

Add your Postgres database as a data source to Grafana. https://grafana.com/docs/grafana/latest/datasources/postgres/
The Database name is most likely just postgres.

## Visualizing data

Create a [dashboard](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/create-dashboard/) with a [timeseries panel](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/time-series/) displaying the values stored in the database.

This is an example query you could use to retrieve the data:
```sql
SELECT time, <other columns>
FROM <table name>
WHERE $__timeFilter(time) 
```

After saving you see a dashboard with the data collected. In the top right you can enable automatic update of the dashboard, if everything is working correctly you can see the new data arriving and being displayed (depending on the setup with 10-60 seconds of delay).