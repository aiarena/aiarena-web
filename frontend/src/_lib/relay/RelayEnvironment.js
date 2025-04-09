// app/relay/RelayEnvironment.js
'use strict';

import { useMemo } from "react";
import { Environment, Network, RecordSource, Store } from "relay-runtime";

let relayEnvironment;

// Define a function that fetches the results of an operation (query/mutation/etc)
// and returns its results as a Promise
function fetchQuery(operation, variables, cacheConfig, uploadables) {
  let apiUrl;
  if (typeof window === "undefined") {
  apiUrl = `${process.env.API_URL}/graphql/`;
} else {
  apiUrl = "/graphql/";
}

  return fetch(apiUrl, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    }, // Add authentication and other headers here
    body: JSON.stringify({
      query: operation.text, // GraphQL text from input
      variables,
    }),
  }).then((response) => response.json());
}

function createEnvironment(initialRecords) {
  return new Environment({
    // Create a network layer from the fetch function
    network: Network.create(fetchQuery),
    store: new Store(new RecordSource(initialRecords)),
  });
}

export function initEnvironment(initialRecords) {
  // For SSR and SSG always create a new Relay environment
  if (typeof window === "undefined") {
    return createEnvironment(initialRecords);
  }

  // Create the Relay environment once in the client
  if (!relayEnvironment) {
    relayEnvironment = createEnvironment(initialRecords);
  }

  // If there are initial records, hydrate the store
  if (initialRecords) {
    relayEnvironment.getStore().publish(new RecordSource(initialRecords));
  }

  return relayEnvironment;
}

export function useEnvironment(initialRecords) {
  const environment = useMemo(
    () => initEnvironment(initialRecords),
    [initialRecords],
  );
  return environment;
}