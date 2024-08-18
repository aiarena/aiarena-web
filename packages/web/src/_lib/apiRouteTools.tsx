import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";

const backendUrl = process.env.NEXT_PUBLIC_API_URL;
const secret = process.env.NEXTAUTH_SECRET;

export async function getBearer(req: NextRequest) {
  const token = await getToken({ req, secret });

  if (!token) {
    return "";
  }
  return token.token as string;
}

export async function parseUrl(url: string) {
  const segments = url.split("/api/tunnel/");

  const beforeApiTunnel = segments[0];
  const apiTunnel = "/api/tunnel/";
  const afterApiTunnel = segments[1];

  if (
    !url ||
    !beforeApiTunnel ||
    !backendUrl ||
    !apiTunnel ||
    !afterApiTunnel
  ) {
    return { error: "missing url", status: 400 };
  }
  const newUrl = `${backendUrl}/${afterApiTunnel}`;
  return { url: newUrl, status: 200 };
}
