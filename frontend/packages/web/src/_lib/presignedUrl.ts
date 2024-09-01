

import { request_get } from "./fetchTools";
import { secure_request_get } from "./secureFetchTools";


//This is currently not used
export const getPresignedUrl = async () => {
    // Fetch the pre-signed URL from SST API
    const response = await request_get({
        url: `${process.env.NEXT_PUBLIC_API_URL}/presigned`,
      });
    
    if (response.status !== 200) {
      throw new Error("Failed to get pre-signed URL");
    }
  
    const url = await response.data.url;
    return {url: url, key: response.data.key, user: response.data.user, id: response.data.id};
  };


  export const getSecurePresignedUrl = async () => {
    const response = await secure_request_get({
      path: `presigned`,
    });
    console.log("response", response)
    if (response.status !== 200) {
      throw new Error("Failed to get pre-signed URL");
    }

    const url = await response.data.url;
    return {url: url, key: response.data.key, user: response.data.user, id: response.data.id};
  }

