# aiarena-web
A website for running the aiarena.net infrastructure.

[See the live website here](https://aiarena.net/)

[Dev Install instructions](./doc/INSTALL.md)

[Frontend](./frontend/README.md)

[Working with infrastructure](./deploy/README.md)

## Module structure:
### /aiarena/core
Core project functionality

### /aiarena/api
Web API endpoints and functionality.  
This root api folder contains views for public use.

#### /aiarena/api/arenaclient
API endpoints specifically for use by the arenaclients to obtain new matches and report results.

#### /aiarena/api/stream
API endpoints specifically for use by the livestream player to obtain a curated list of match replays to feature.

### /aiarena/frontend
Django template website frontend

### /aiarena/frontend-spa
React frontend for the profile dashboard

### /aiarena/graphql
GraphQL API used by the React frontend

### /aiarena/patreon
A module for linking website users to their patreon counterparts.

### /frontend
Next.JS / Tailwind frontend using GraphQL

## License

Copyright (c) 2019

Licensed under the [GPLv3 license](LICENSE).