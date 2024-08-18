import "sst/node/config";
declare module "sst/node/config" {
  export interface ConfigTypes {
    APP: string;
    STAGE: string;
  }
}import "sst/node/config";
declare module "sst/node/config" {
  export interface SecretResources {
    "STRIPE_SECRET_KEY": {
      value: string;
    }
  }
}import "sst/node/api";
declare module "sst/node/api" {
  export interface ApiResources {
    "Api": {
      url: string;
    }
  }
}import "sst/node/site";
declare module "sst/node/site" {
  export interface NextjsSiteResources {
    "site": {
      url: string;
    }
  }
}