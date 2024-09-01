import React, { useEffect, useState } from 'react';

const CompetitionData: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchGraphQLData() {
      try {
        const query = `
          {
            competitions(status: OPEN) {
              edges {
                node {
                  name
                  url
                  participants(first: 10) {
                    edges {
                      node {
                        bot {
                          name
                          url
                          user {
                            patreonLevel
                          }
                        }
                        elo
                        trend
                        divisionNum
                      }
                    }
                  }
                }
              }
            }
            bots(first: 15, orderBy: "-bot_zip_updated") {
              edges {
                node {
                  name
                  botZipUpdated
                }
              }
            }
            news {
              edges {
                node {
                  title
                  ytLink
                  created
                }
              }
            }
          }
        `;

        console.log('Sending POST request with query:', query);  // Log the query being sent

        const response = await fetch('/api/proxy', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        console.log('Received response:', response);  // Log the response object

        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('Received data:', result);  // Log the received data
        setData(result);
      } catch (error: any) {
        console.error('Fetch error:', error.message);  // Log any errors
        setError(error.message || 'An error occurred while fetching data');
      }
    }

    fetchGraphQLData();
  }, []);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {/* Render your data here */}
    </div>
  );
};

export default CompetitionData;
