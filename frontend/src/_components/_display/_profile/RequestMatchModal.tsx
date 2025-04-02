import React, { useState } from "react";
import Modal from "../Modal";
import { graphql, useLazyLoadQuery } from "react-relay";
import { RequestMatchModalBot1Query } from "./__generated__/RequestMatchModalBot1Query.graphql";
import SelectSearch from "@/_components/_props/SearchSelectList";

import { RequestMatchModalBot2Query } from "./__generated__/RequestMatchModalBot2Query.graphql";
import { RequestMatchModalMapPoolQuery } from "./__generated__/RequestMatchModalMapPoolQuery.graphql";
import { RequestMatchModalSpecificMapQuery } from "./__generated__/RequestMatchModalSpecificMapQuery.graphql";

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

interface Option {
  id: string;
  label: string;
}

interface SearchOrSelectValue {
  select: string;
  searchAndDisplay: string;
}

interface UploadBotModal {
  isOpen: boolean;
  onClose: () => void;
}

export default function RequestMatchModal({ isOpen, onClose }: UploadBotModal) {
  const [bot1IsSearching, setBot1IsSearching] = useState(false);
  const [bot1SearchTerm, setBot1SearchTerm] = useState("");

  const [bot2IsSearching, setBot2IsSearching] = useState(false);
  const [bot2SearchTerm, setBot2SearchTerm] = useState("");

  const [mapSelectionType, setMapSelectionType] = useState("specific_map");

  const [specificMapIsSearching, setSpecificMapIsSearching] = useState(false);
  const [specificMapSearchTerm, setSpecificMapSearchTerm] = useState("");

  const [mapPoolIsSearching, setMapPoolIsSearching] = useState(false);
  const [mapPoolSearchTerm, setMapPoolSearchTerm] = useState("");

  const [matchCount, setMatchCount] = useState(1);

  const [bot1SearchOrSelect, setBot1SearchOrSelect] =
    useState<SearchOrSelectValue>({
      select: "",
      searchAndDisplay: "",
    });

  const [bot2SearchOrSelect, setBot2SearchOrSelect] =
    useState<SearchOrSelectValue>({
      select: "",
      searchAndDisplay: "",
    });

  const [specificMapSearchOrSelect, setSpecificMapSearchOrSelect] =
    useState<SearchOrSelectValue>({
      select: "",
      searchAndDisplay: "",
    });

  const [mapPoolSearchOrSelect, setMapPoolSearchOrSelect] =
    useState<SearchOrSelectValue>({
      select: "",
      searchAndDisplay: "",
    });

  const [queryVariablesBot1, setQueryVariablesBot1] = useState({ name: "" });
  const [queryVariablesBot2, setQueryVariablesBot2] = useState({ name: "" });
  const [queryVariablesSpecificMap, setQueryVariablesSpecificMap] = useState({
    name: "",
  });
  const [queryVariablesMapPool, setQueryVariablesMapPool] = useState({
    name: "",
  });

  const handleBot1Search = (term: string) => {
    setBot1IsSearching(true);
    setBot1SearchTerm(term);
  };

  const handleBot2Search = (term: string) => {
    setBot2IsSearching(true);
    setBot2SearchTerm(term);
  };

  const handleSpecificMapSearch = (term: string) => {
    setBot2IsSearching(true);
    setBot2SearchTerm(term);
  };

  const handleMapPoolSearch = (term: string) => {
    setBot2IsSearching(true);
    setBot2SearchTerm(term);
  };

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setQueryVariablesBot1({ name: bot1SearchTerm });
    }, 1000);

    return () => clearTimeout(timer);
  }, [bot1SearchTerm]);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setQueryVariablesBot2({ name: bot2SearchTerm });
    }, 1000);

    return () => clearTimeout(timer);
  }, [bot2SearchTerm]);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setQueryVariablesSpecificMap({ name: specificMapSearchTerm });
    }, 1000);

    return () => clearTimeout(timer);
  }, [specificMapSearchTerm]);

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setQueryVariablesMapPool({ name: mapPoolSearchTerm });
    }, 1000);

    return () => clearTimeout(timer);
  }, [mapPoolSearchTerm]);

  const bot1Data = useLazyLoadQuery<RequestMatchModalBot1Query>(
    graphql`
      query RequestMatchModalBot1Query($name: String) {
        bots(name: $name, first: 10) {
          edges {
            node {
              id
              name
              created
              botZipUpdated
              user {
                id
                username
              }
            }
          }
        }
      }
    `,
    queryVariablesBot1,
    { fetchPolicy: "network-only" }
  );

  const bot2Data = useLazyLoadQuery<RequestMatchModalBot2Query>(
    graphql`
      query RequestMatchModalBot2Query($name: String) {
        bots(name: $name, first: 10) {
          edges {
            node {
              id
              name
              created
              botZipUpdated
              user {
                id
                username
              }
            }
          }
        }
      }
    `,
    queryVariablesBot2,
    { fetchPolicy: "network-only" }
  );

  const specificMapData = useLazyLoadQuery<RequestMatchModalSpecificMapQuery>(
    graphql`
      query RequestMatchModalSpecificMapQuery($name: String) {
        maps(name: $name, first: 10) {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    `,
    queryVariablesSpecificMap,
    { fetchPolicy: "network-only" }
  );

  const mapPoolData = useLazyLoadQuery<RequestMatchModalMapPoolQuery>(
    graphql`
      query RequestMatchModalMapPoolQuery($name: String) {
        mapPools(name: $name, first: 10) {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    `,
    queryVariablesMapPool,
    { fetchPolicy: "network-only" }
  );

  React.useEffect(() => {
    if (bot1Data) {
      setBot1IsSearching(false);
    }
  }, [bot1Data]);

  React.useEffect(() => {
    if (bot2Data) {
      setBot2IsSearching(false);
    }
  }, [bot2Data]);
  React.useEffect(() => {
    if (specificMapData) {
      setSpecificMapIsSearching(false);
    }
  }, [specificMapData]);

  React.useEffect(() => {
    if (mapPoolData) {
      setMapPoolIsSearching(false);
    }
  }, [mapPoolData]);

  const bot1Options = React.useMemo(() => {
    if (!bot1Data?.bots?.edges) return [];

    return bot1Data.bots.edges
      .map((edge) => {
        if (!edge?.node) return null;
        const bot = edge.node;
        return {
          id: bot.id,
          label: `${bot.name} (by ${bot.user?.username || "Unknown"})`,
        };
      })
      .filter(Boolean) as Option[];
  }, [bot1Data]);
  const bot2Options = React.useMemo(() => {
    if (!bot2Data?.bots?.edges) return [];

    return bot2Data.bots.edges
      .map((edge) => {
        if (!edge?.node) return null;
        const bot = edge.node;
        return {
          id: bot.id,
          label: `${bot.name} (by ${bot.user?.username || "Unknown"})`,
        };
      })
      .filter(Boolean) as Option[];
  }, [bot2Data]);
  const specificMapOptions = React.useMemo(() => {
    if (!specificMapData?.maps?.edges) return [];

    return specificMapData.maps.edges
      .map((edge) => {
        if (!edge?.node) return null;
        const map = edge.node;
        return {
          id: map.id,
          label: `${map.name}`,
        };
      })
      .filter(Boolean) as Option[];
  }, [specificMapData]);
  const mapPoolOptions = React.useMemo(() => {
    if (!mapPoolData?.mapPools?.edges) return [];

    return mapPoolData.mapPools.edges
      .map((edge) => {
        if (!edge?.node) return null;
        const mapPool = edge.node;
        return {
          id: mapPool.id,
          label: `${mapPool.name}`,
        };
      })
      .filter(Boolean) as Option[];
  }, [mapPoolData]);

  const handleRequestMatch = () => {};

  if (!isOpen) return null;

  return (
    <Modal onClose={onClose} title="Request Match">
      <div className="space-y-4">
        <div className="mb-4">
          <label className="block text-left font-medium mb-1">Bot 1</label>
          <SelectSearch
            options={bot1Options}
            searchOrSelect={bot1SearchOrSelect}
            onChange={(value) => {
              setBot1SearchOrSelect(value);

              if (value.select) {
                setBot1SearchTerm(value.searchAndDisplay);
              }
            }}
            onSearch={handleBot1Search}
            isLoading={bot1IsSearching}
            placeholder="Search for bots..."
          />
        </div>
        <div className="mb-4">
          <label className="block text-left font-medium mb-1">Bot 2</label>
          <SelectSearch
            options={bot2Options}
            searchOrSelect={bot2SearchOrSelect}
            onChange={(value) => {
              setBot2SearchOrSelect(value);

              if (value.select) {
                setBot2SearchTerm(value.searchAndDisplay);
              }
            }}
            onSearch={handleBot2Search}
            isLoading={bot2IsSearching}
            placeholder="Search for bots..."
          />
        </div>{" "}
        <div className="">
          <div>
            <button
              onClick={() => {
                setMapSelectionType("specific_map");
              }}
              className={`${mapSelectionType == "specific_map" ? "bg-customGreen" : null} p-2`}
            >
              Specific Map
            </button>{" "}
            <button
              onClick={() => {
                setMapSelectionType("map_pool");
              }}
              className={`${mapSelectionType == "map_pool" ? "bg-customGreen" : null} p-2`}
            >
              Map Pool
            </button>
          </div>
        </div>
        <div>
          {mapSelectionType == "specific_map" ? (
            <div className="mb-4">
              <label className="block text-left font-medium mb-1">
                Specific Map
              </label>
              <SelectSearch
                options={specificMapOptions}
                searchOrSelect={specificMapSearchOrSelect}
                onChange={(value) => {
                  setSpecificMapSearchOrSelect(value);

                  if (value.select) {
                    setSpecificMapSearchTerm(value.searchAndDisplay);
                  }
                }}
                onSearch={handleSpecificMapSearch}
                isLoading={specificMapIsSearching}
                placeholder="Search for specific map..."
              />
            </div>
          ) : null}
          {mapSelectionType == "map_pool" ? (
            <div className="mb-4">
              <label className="block text-left font-medium mb-1">
                Map pool
              </label>
              <SelectSearch
                options={mapPoolOptions}
                searchOrSelect={mapPoolSearchOrSelect}
                onChange={(value) => {
                  setMapPoolSearchOrSelect(value);

                  if (value.select) {
                    setMapPoolSearchTerm(value.searchAndDisplay);
                  }
                }}
                onSearch={handleMapPoolSearch}
                isLoading={mapPoolIsSearching}
                placeholder="Search for map pool..."
              />
            </div>
          ) : null}
        </div>
        <br />
        <br />
        Match Count:{" "}
        <input
          value={matchCount}
          type="number"
          className="text-black text-right w-10"
          onChange={(e) => setMatchCount(parseInt(e.target.value))}
        ></input>
        <button
          onClick={handleRequestMatch}
          className="w-full bg-customGreen text-white py-2 rounded"
        >
          Request match
        </button>
      </div>
    </Modal>
  );
}
