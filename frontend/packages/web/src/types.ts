export interface Bot {
    name: string;
  }
  
  export interface Participant {
    bot: Bot;
    elo: number;
    trend: number;
    divisionNum: number;
  }
  
  export interface CompetitionNode {
    name: string;
    participants: {
      edges: { node: Participant }[];
    };
  }
  
  export interface Competition {
    node: CompetitionNode;
  }
  
  export interface NewsNode {
    title: string;
    ytLink: string;
    created: string;
  }
  
  export interface News {
    node: NewsNode;
  }
  
  export interface ApiResponse {
    competitions: {
      edges: Competition[];
    };
    news: {
      edges: News[];
    };
  }
  