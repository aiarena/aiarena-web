import type { BrowserHistory, Location } from "history";
import { createBrowserHistory } from "history";
import React, { useCallback, useLayoutEffect, useRef, useState } from "react";
import { Router } from "react-router";

interface SmartRouterProps {
  basename?: string;
  children?: React.ReactNode;
}

function locationString(
  locationLike: Parameters<BrowserHistory["push"]>[0],
): string {
  if (typeof locationLike === "string") {
    return locationLike;
  }
  const { pathname, search, hash } = locationLike;
  let result = pathname || "";

  if (search) {
    result += search.startsWith("?") ? search : `?${search}`;
  }
  if (hash) {
    result += hash.startsWith("#") ? hash : `#${hash}`;
  }
  return result;
}

function createSmartHistory(): BrowserHistory {
  const history = createBrowserHistory();
  const origPush = history.push;

  history.push = (path, state) => {
    if (window.buildNumbersMismatch) {
      window.location.href = locationString(path);
    } else {
      origPush(path, state);
    }
  };

  return history;
}

export function SmartRouter({ basename, children }: SmartRouterProps) {
  const historyRef = useRef<BrowserHistory>(null);
  if (historyRef.current == null) {
    historyRef.current = createSmartHistory();
  }

  const history = historyRef.current;
  const [state, setStateImpl] = useState({
    action: history.action,
    location: history.location,
  });

  const setState = useCallback(
    (newState: { action: BrowserHistory["action"]; location: Location }) => {
      React.startTransition(() => setStateImpl(newState));
    },
    [],
  );

  useLayoutEffect(() => history.listen(setState), [history, setState]);

  return (
    <Router
      basename={basename}
      // biome-ignore lint/correctness/noChildrenProp: mirror react-router impl
      children={children}
      location={state.location}
      navigationType={state.action}
      navigator={history}
    />
  );
}
