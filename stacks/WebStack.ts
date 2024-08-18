import { StackContext, NextjsSite, use } from "sst/constructs";
import { ApiStack } from "stacks/ApiStack";



interface ApiStack {
  url: string;
}

interface AuthStack {
  userPoolId: string;
  userPoolClientId: string;
  cognitoIdentityPoolId: string;
}

interface StorageStack {
  bucketName: string;
  tableName: string;
}

export function WebStack({ stack }: StackContext) {
  const { api } = use(ApiStack);

  const site = new NextjsSite(stack, "site", {
    path: "packages/web",
    runtime: "nodejs20.x",

    environment: {
      NEXT_PUBLIC_API_URL: api.url,
      NEXT_PUBLIC_REGION: stack.region,
      NEXT_PUBLIC_SITE_URL: "http://localhost:3000",
    },
  });
  stack.addOutputs({
    NEXT_PUBLIC_SITE_URL1: site.url,
    NEXT_PUBLIC_SITE_URL: site.url || "localhost:3000",
  });
}
