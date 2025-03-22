import axios from 'axios';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const graphqlUrl = 'https://aiarena.net/graphql/';

    const { query } = await req.json();

    if (!query) {
      return NextResponse.json({ error: 'Query parameter is required' }, { status: 400 });
    }

    // Set up the cookies and headers including the Referer header
    const headers = {
      'Content-Type': 'application/json',
      'Cookie': 'csrftoken=ylRBBnzSvJ7sb6TxEfzFFEZxPxwOVqf6; _pk_id.1.f54c=272103cf52395e28.1723544578.; _ga=GA1.2.293885153.1723544578; sessionid=lw7xa06592gm08egtnmwq1dus7g9mtgs; _pk_ref.1.f54c=%5B%22%22%2C%22%22%2C1724176994%2C%22https%3A%2F%2Fd31c83tipf4wh7.cloudfront.net%2F%22%5D',
      'X-CSRFToken': 'ylRBBnzSvJ7sb6TxEfzFFEZxPxwOVqf6', // Include the CSRF token header
      'Referer': 'https://aiarena.net/',  // Include the Referer header
    };

    const response = await axios.post(
      graphqlUrl,
      { query },
      { headers }
    );

    return NextResponse.json(response.data, { status: response.status });
  } catch (error: any) {
    console.error('Proxy error:', error.message);
    return NextResponse.json({ error: error.message || 'Server error' }, { status: error.response?.status || 500 });
  }
}
