import Footer from "@/_components/_nav/Footer";
import Navbar from "@/_components/_nav/Navbar";

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className="flex flex-col min-h-screen ">
        <Navbar />

        <main className="flex-grow bg-darken">{children}</main>

        <Footer />
      </div>
    </>
  );
}

export default Layout;
