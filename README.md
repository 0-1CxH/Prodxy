
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

```text
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


Then, building the query synthesis pipeline is easy as filling the Prodxy graph with operations:

```mermaid
stateDiagram-v2
    state "general_destination_city: sample a city name from property 'city', or nothing" as general_destination_city
    state "general_source_city: sample a city name from property 'cities' that is different from destination, or nothing" as general_source_city
    state "departure_date_format: random set flag of date format (relative, absolute, range)" as departure_date_format
    state "relative_departure_date: generate a relative departure date" as relative_departure_date
    state "absolute_departure_date: generate an absolute departure date" as absolute_departure_date
    state "departure_date_range: generate two dates and form a range" as departure_date_range
    state "specific_method: set flag of method description (implicit, explicit)" as specific_method
    state "explicit_method: set flag of explicit method name (train, flight)" as explicit_method
    state "implicit_method: set flag of implicit method name (train, flight)" as implicit_method
    state "specific_train_stations: sample one or two train station from property 'station' with the given destination (or plus source) city name" as specific_train_stations
    state "specific_airports: sample an airport from property 'airport' with the given destination (or plus source) city name" as specific_airports
    state "train_personal_demands: sample zero to many personal demand(s) from property 'pref_for_train'" as train_personal_demands
    state "flight_personal_demands: sample zero to many personal demand(s) from property 'pref_for_flight'" as flight_personal_demands
    state "finalization: call LLM to get final synthetic query(s) based on the given flags and properties, then save everything" as finalization

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

And, the rollout evaluation pipeline will still use the Prodxy graph, but filling with another set of operations:

