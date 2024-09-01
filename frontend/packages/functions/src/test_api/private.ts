import { APIGatewayProxyHandlerV2WithJWTAuthorizer } from "aws-lambda";

// A simple private api response using JWT for authentication

export const main: APIGatewayProxyHandlerV2WithJWTAuthorizer = async (
  event
) => {
  return {
    statusCode: 200,
    body: `Hello ${event.requestContext.authorizer.jwt.claims.sub}!`,
  };
};
