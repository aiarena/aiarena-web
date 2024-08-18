import { Config, StackContext, Api, use } from "sst/constructs";


export function ApiStack({ stack, app }: StackContext) {

  const STRIPE_SECRET_KEY = new Config.Secret(stack, "STRIPE_SECRET_KEY");
  const api = new Api(stack, "Api", {

    defaults: {
      authorizer: "none",
    },
   

    cors: true,
    routes: {

      
      "GET /private": "packages/functions/src/test_api/private.main",
      "GET /public": {
        function: "packages/functions/src/test_api/public.main",
        authorizer: "none",
      }
    },
  });

  stack.addOutputs({
    ApiEndpoint: api.url,
  });

  return {
    api,
  };
}


//handle cors from handler.js in core
