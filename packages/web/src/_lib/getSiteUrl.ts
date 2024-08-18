"use client";

export function getSiteUrl() {
  if (typeof window === "undefined") return null;
  if (typeof window.location === "undefined") return null;

  // Parsing the NEXTAUTH_URL_INTERNAL
  const parsedUrl = new URL(process.env.NEXT_PUBLIC_SITE_URL as string);


  // Extracting protocol, hostname, and port from the URL
  const defaultProtocol = parsedUrl.protocol + "//";
  const defaultHostname = parsedUrl.hostname;
  const defaultPort = parsedUrl.port ? `:${parsedUrl.port}` : '';

  // Extract values from the window.location
  const protocol = window.location.protocol + "//";
  const hostname = window.location.hostname;
  const port = window.location.port ? `:${window.location.port}` : '';

  // Use defaults if values from window.location are empty or localhost
  const finalProtocol = hostname === "localhost" ? defaultProtocol : protocol;
  const finalHostname = hostname === "localhost" ? defaultHostname : hostname;
  const finalPort = (port === "" && hostname !== "localhost") ? "" : (port || defaultPort);

  return `${finalProtocol}${finalHostname}${finalPort}`;
}
