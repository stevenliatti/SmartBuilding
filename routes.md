# KNX

## Commands


### open_blinds

- Method: GET
- Endpoint: "/open_blinds"
- Params:
    - uuid: string
    - major: int
    - minor: int
- Response OK: `{ success: true }`
- Error: `{ success: false }`


### close_blinds

- Method: GET
- Endpoint: "/close_blinds"
- Params:
    - uuid: string
    - major: int
    - minor: int
- Response OK: `{ success: true }`
- Error: `{ success: false }`


### percentage_blinds

- Method: GET
- Endpoint: "/percentage_blinds"
- Params:
    - uuid: string
    - major: int
    - minor: int
    - percentage: int
- Response OK: `{ success: true }`
- Error: `{ success: false }`


### percentage_radiator

- Method: GET
- Endpoint: "/percentage_radiator"
- Params:
    - uuid: string
    - major: int
    - minor: int
    - percentage: int
- Response OK: `{ success: true }`
- Error: `{ success: false }`


## Infos


### read_percentage_blinds

- Method: GET
- Endpoint: "/read_percentage_blinds"
- Params:
    - uuid: string
    - major: int
    - minor: int
- Response OK: `{ success: true, percentage: 42 }`
- Error: `{ success: false }`



# OpenZWave

## Commands


### percentage_dimmers

- Method: GET
- Endpoint: "/percentage_dimmers"
- Params:
    - uuid: string
    - major: int
    - minor: int
    - percentage: int
- Response OK: `{ success: true }`
- Error: `{ success: false }`


## Infos


### get_network_info

- Method: GET
- Endpoint: "/get_network_info"
- Params:
    - uuid: string
    - major: int
    - minor: int
- Response OK: `{ success: true, info: ... }`
- Error: `{ success: false }`


### get_nodes_list

- Method: GET
- Endpoint: "/get_nodes_list"
- Params:
    - uuid: string
    - major: int
    - minor: int
- Response OK: `{ success: true, info: ... }`
- Error: `{ success: false }`

