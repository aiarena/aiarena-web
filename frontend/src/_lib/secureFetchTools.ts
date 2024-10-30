
import axios, { AxiosResponse } from "axios";
import handleError from "./handleError";
import { getSiteUrl } from "./getSiteUrl";

interface GetOptions {
    path: string;
    
  }

interface GetResponse {
  data: any, 
  status: number
}
  
  export async function secure_request_get({ path }: GetOptions): Promise<GetResponse> {
    const url = getSiteUrl(); // replace this with a definitive url in production
      return axios
        .get(`${url}/api/tunnel/${path}`, {
        })
        .then((response) => {
          if (response.status === 200) {
            console.log("get returned response", response)
            return {data: response.data.response, status: response.status};
          } else {
            handleError({ message: response.statusText });
            throw new Error(response.statusText); // Throw an error
          }
        })
        .catch((error) => {
          handleError({ error: error });
          throw error; // Re-throw the error to propagate it
        });

  }

interface PostOptions {
  path: string;
  data: any;
  additionalHeaders?: Record<string, string>;
  
}

interface PostResponse {
  data: any, 
  status: number
}

export async function secure_request_post({
  path,
  data,
  additionalHeaders = {},
  
}: PostOptions): Promise<PostResponse> {
  const url = getSiteUrl();
      
    return axios
      .post(`${url}/api/tunnel/${path}`, data, {
        // headers: {
        //   ContentType: "application/json",
        //   ...additionalHeaders,
        // },
      })
      .then((response) => {
        if (response.status === 200) {
          console.log("post returned response", response)
          return {data: response.data.response, status: response.status};
        } else {
          handleError({ message: response.statusText });
          throw new Error(response.statusText); // Throw an error
        }
      })
      .catch((error) => {
        handleError({ error: error });
        throw error; // Re-throw the error to propagate it
      });
  // });
}


interface DeleteOptions {
  path: string;
}

interface DeleteResponse {
  data: any, 
  status: number
}

export async function secure_request_delete({ path }: DeleteOptions): Promise<DeleteResponse> {
  const url = getSiteUrl();
    return axios
      .delete(`${url}/api/tunnel/${path}`)
      .then((response) => {
        if (response.status === 200) {
          return {data: response.data.response, status: response.status};
        } else {
          handleError({ message: response.statusText });
          throw new Error(response.statusText); // Throw an error
        }
      })
      .catch((error) => {
        handleError({ error: error });
        throw error; // Re-throw the error to propagate it
      });
}
