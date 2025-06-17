export const CONNECTION_KEYS = {
    UserMatchRequestsConnection: "UserMatchRequestsConnection",
    UserBotsConnection: "UserBotsConnection",
} as const;

export type ConnectionKey = keyof typeof CONNECTION_KEYS;
export type ConnectionIDMap = {
    [K in ConnectionKey]?: string;
};