import {
  RequestParameters,
  CacheConfig,
  Variables,
  UploadableMap,
  Environment,
  Network,
  RecordSource,
  Store,
} from "relay-runtime";

import fetchGraphQL from "./fetchGraphQL";

async function fetchRelay(
  params: RequestParameters,
  variables: Variables,
  _cacheConfig: CacheConfig,
  uploadables?: UploadableMap | null,
) {
  return fetchGraphQL(params.text, variables, uploadables);
}

export default new Environment({
  network: Network.create(fetchRelay),
  store: new Store(new RecordSource()),
});
