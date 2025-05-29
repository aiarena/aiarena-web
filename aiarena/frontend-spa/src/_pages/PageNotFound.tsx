import { Link } from "react-router";

export default function PageNotFound() {
  return (
    <div className="flex flex-col items-center justify-center flex-grow text-center relative min-h-[60em]">
      <h1
        className="text-9xl font-extrabold tracking-widest relative"
        aria-label="Error 404: Page Not Found"
      >
        404
        <span
          className="border-4  border-customGreen bg-neutral-900 px-3 py-1 text-sm font-semibold tracking-normal rounded rotate-6 absolute top-16 left-1/2 transform -translate-x-1/2 whitespace-nowrap"
          aria-hidden="true"
        >
          Page Not Found
        </span>
      </h1>
      <p className="text-lg mt-12 mb-10">
        Sorry, we couldn&apos;t find the page you&apos;re looking for.
      </p>
      <Link to="/dashboard/">
        <span
          className="hover:border-4 border-4 border-customGreen bg-neutral-900 hover:bg-transparent hover:border-customGreen text-white font-semibold py-3 px-8 rounded-full shadow-lg transition duration-300 ease-in-out transform"
          aria-label="Navigate back to the main dashboard with your bots"
        >
          Back to Bots
        </span>
      </Link>
    </div>
  );
}
