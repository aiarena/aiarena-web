## AI Arena frontend using Next.JS, Tailwind and Relay

## Getting Started

1. First - Follow the backend dev enviornment install instructions:
   [Dev Install instructions](./doc/INSTALL.md)

2. In your backend environment, run:

```bash
python manage.py graphql_schema
# to generate the GraphQL schema, then do
python manage.py runserver
# to start the backend development server
```

3. Navigate to the frontend directory and install dependencies:

```bash
cd frontend
# install required packages
npm i
```

4. Run the frontend development server:

```bash
npm run relay
# To start the GraphQL relay, then, in a seperate terminal, run:
npm run dev
```

The frontend should be available at
[http://localhost:3000]

The Graphql API should be available at
[http://localhost:8000/graphql]

Errors:
If you get a watchman error when running npm run relay:

- You can either install watchman.
  Or
- Remove --watch from the "npm run relay" command:
  "relay": "relay-compiler --watch",
