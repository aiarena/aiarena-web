import { Outlet } from "react-router";

export default function Layout() {
  return (
    <div className="flex flex-col min-h-screen font-sans bg-background-texture">
      Navbar will be here
      <Outlet />
      Footer will be here
    </div>
  );
}
