import {
  Environment,
  Network,
  RecordSource,
  Store,
} from "relay-runtime";

import fetchGraphQL from "./fetchGraphQL";

async function fetchRelay(params, variables, cacheConfig, uploadables) {
  return fetchGraphQL(params.text, variables, uploadables);
}

export default new Environment({
  network: Network.create(fetchRelay),
  store: new Store(new RecordSource()),
});
