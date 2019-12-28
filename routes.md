# KNX

## Commands

- GET, "/open_blinds", params_url: { uuid: string, major: int, minor: int }
- GET, "/close_blinds", params_url: { uuid: string, major: int, minor: int }
- GET, "/percentage_blinds", params_url: { uuid: string, major: int, minor: int, percentage: int }
- GET, "/percentage_radiator", params_url: { uuid: string, major: int, minor: int, percentage: int }

## Infos

- GET, "/read_percentage_blinds", params_url: { uuid: string, major: int, minor: int }


# OpenZWave

## Commands

- GET, "/percentage_dimmers", params_url: { uuid: string, major: int, minor: int, percentage: int }

## Infos

- GET, "/get_network_info", params_url: { uuid: string, major: int, minor: int }
- GET, "/get_nodes_list", params_url: { uuid: string, major: int, minor: int }
