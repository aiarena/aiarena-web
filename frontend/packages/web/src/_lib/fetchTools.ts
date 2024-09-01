import axios, { AxiosResponse } from "axios";
import handleError from "./handleError";

interface PostOptions {
  url: string;
  data: any;
  additionalHeaders?: Record<string, string>;
  secret: string;
}

export async function request_post({
  url,
  data,
}: PostOptions): Promise<AxiosResponse<any>> {
  return axios
    .post(`${url}`, data, {})
    .then((response) => {
      if (response.status === 200) {
        return response;
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

interface GetOptions {
  url: string;
}

export async function request_get({
  url,
}: GetOptions): Promise<AxiosResponse<any>> {
  return axios
    .get(`${url}`, {})
    .then((response) => {
      if (response.status === 200) {
        return response;
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

interface DeleteOptions {
  url: string;
}

export async function request_delete({
  url,
}: DeleteOptions): Promise<AxiosResponse<any>> {
  return axios
    .delete(`${url}`, {})
    .then((response) => {
      if (response.status === 200) {
        return response;
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
