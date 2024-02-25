# Integration Tests

This directory contains tools for conducting arena client integration tests with aiarena-web. These tools are handy for catching hard to debug issues, such as race conditions in the AC API.
- `mock_ac.py` - contains a mock arena client which can be spawned and used to simulate the behavior of a real arena client.
- `run_acs.py` - will spawn a specified number of mock arena clients and run them in parallel. This is useful for testing the website's behavior under load.

## Running the test

### Seed the database
Run the integration tests django seed command like so:
```bash
python manage.py seed_integration_tests --numacs 10
```
Be sure to specify enough arena clients to run the test you want to run.

### Run the test
Run the `run_acs.py` script to start 10 mock arena clients, running a total of 1000 matches.
```bash
python ./run_acs.py
```

You can customize the number of mock arena clients and the number of matches to run by passing in the `--numacs` and `--nummatches` flags, respectively:
```bash
python ./run_acs.py --numacs 20 --nummatches 5000
```

