import { useState, useEffect } from 'react';
import { secure_request_get } from '@/_lib/secureFetchTools';
import handleError from '@/_lib/handleError';

interface FetchResult {
  data: string | null;
  isLoading: boolean;
  error: string | null;
}

export function useSecureFetchText(path: string): FetchResult {
  const [data, setData] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    secure_request_get({ path: path })
      .then((response) => {
        if (!response) {
          handleError(response);
          throw new Error('Fetch error');
        }
        return response.data;
      })
      .then((data) => {
        setData(data); 
        setIsLoading(false);
      })
      .catch((error) => {
        setError(error.toString());
        setIsLoading(false);
      });
  }, [path]);

  return { data, isLoading, error };
};