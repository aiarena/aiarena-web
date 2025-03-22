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

        const response = await fetch('/api/proxy', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }

        const result = await response.json();
        setData(result);
      } catch (error: any) {
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
