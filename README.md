
## Env 

```python>=3.10``` is required.

There are some packages required:

```
langgraph
jsonpath_ng
```

These packages are optional:

```
grandalf
```


## Example

### `examples/search_flights_and_trains.yaml`

The example demostrates an LLM agent product's business scene 'search flights and trains', which is described as follows: 

```
- User must give a specific destination city in text query, but giving a source city in text query is optional, location context is used if not.
- User can choose to point out the departure date, relative date or date range in text query, if not, use today.
- User might or might not specify the method (flight or train) by directly clarification or by specify the airport name, train station name of source / destination city in text query, if is the latter case, the city is implied.
- User can have extra demands, such as first-class cabin, meal included, or WiFi connection for the flight or train trip.
```

The Prodxy graph is designed as:

```mermaid
stateDiagram-v2
    [*] --> general_destination_city
    general_destination_city --> finalization : not given
    general_destination_city --> general_source_city : given
    general_source_city --> departure_date_format

    departure_date_format --> relative_departure_date: relative
    relative_departure_date --> specific_method
    departure_date_format --> absolute_departure_date: absolute
    absolute_departure_date --> specific_method
    departure_date_format --> departure_date_range: range
    departure_date_range --> specific_method
    
    specific_method --> explicit_method
    specific_method --> implicit_method
    
    explicit_method --> train_personal_demands: train
    explicit_method --> flight_personal_demands: flight
    
    implicit_method --> specific_train_stations: train
    implicit_method --> specific_airports: flight

    
    specific_train_stations --> train_personal_demands
    specific_airports --> flight_personal_demands

    train_personal_demands --> finalization
    flight_personal_demands --> finalization
    finalization --> [*]
```


Then, the query synthesis pipeline is:

```mermaid
stateDiagram-v2
    state "general_destination_city\n(Sample a city name from 'city' or nothing)" as general_destination_city
    state "general_source_city\n(Sample a different city from 'cities' or nothing)" as general_source_city
    state "departure_date_format\n(Randomly set flag: relative, absolute, range)" as departure_date_format
    state "relative_departure_date\n(Generate a relative departure date)" as relative_departure_date
    state "absolute_departure_date\n(Generate an absolute departure date)" as absolute_departure_date
    state "departure_date_range\n(Generate two dates to form a range)" as departure_date_range
    state "specific_method\n(Set method description flag: implicit, explicit)" as specific_method
    state "explicit_method\n(Set explicit method name: train, flight)" as explicit_method
    state "implicit_method\n(Set implicit method name: train, flight)" as implicit_method
    state "specific_train_stations\n(Sample train stations from 'station' property)" as specific_train_stations
    state "specific_airports\n(Sample an airport from 'airport' property)" as specific_airports
    state "train_personal_demands\n(Sample demands from 'pref_for_train')" as train_personal_demands
    state "flight_personal_demands\n(Sample demands from 'pref_for_flight')" as flight_personal_demands
    state "finalization\n(Call LLM for final query and save results)" as finalization

    [*] --> general_destination_city
    general_destination_city --> finalization : not given
    general_destination_city --> general_source_city : given
    general_source_city --> departure_date_format

    departure_date_format --> relative_departure_date: relative
    relative_departure_date --> specific_method
    departure_date_format --> absolute_departure_date: absolute
    absolute_departure_date --> specific_method
    departure_date_format --> departure_date_range: range
    departure_date_range --> specific_method
    
    specific_method --> explicit_method
    specific_method --> implicit_method
    
    explicit_method --> train_personal_demands: train
    explicit_method --> flight_personal_demands: flight
    
    implicit_method --> specific_train_stations: train
    implicit_method --> specific_airports: flight

    specific_train_stations --> train_personal_demands
    specific_airports --> flight_personal_demands

    train_personal_demands --> finalization
    flight_personal_demands --> finalization
    finalization --> [*]
```

and, the rollout evaluation pipeline 