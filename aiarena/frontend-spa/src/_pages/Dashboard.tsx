import LoadingSpinnerGray from "@/_components/_display/LoadingSpinnerGray";
import { useEffect } from "react";
import { useNavigate } from "react-router";

export default function Dashboard() {
  const navigate = useNavigate();
  useEffect(() => {
    navigate("userbots");
  }, [navigate]);

  return (
    <div>
      <LoadingSpinnerGray />
    </div>
  );
}
